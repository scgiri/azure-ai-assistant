# Azure App Registration & Federated Identity Setup

This guide walks you through every manual step required on the Azure Portal to
configure OIDC-based authentication between **GitHub Actions** and **Azure**.
Once complete, your CI/CD pipelines can deploy to Azure **without storing any
passwords or client secrets** in GitHub.

---

## Architecture Overview

```
┌──────────────────────┐         ┌───────────────────────────────────┐
│   GitHub Actions      │         │  Microsoft Entra ID (Azure AD)    │
│                      │         │                                   │
│  Workflow requests   │ ──(1)──▶│  Validate OIDC token against      │
│  an OIDC token from  │         │  Federated Identity Credentials   │
│  GitHub's token      │         │                                   │
│  endpoint            │         │  ┌─────────────────────────────┐  │
│                      │         │  │ App Registration             │  │
│                      │         │  │  ├─ Client ID                │  │
│                      │         │  │  ├─ Tenant ID                │  │
│                      │         │  │  └─ Federated Credentials    │  │
│                      │         │  │      ├─ branch: main         │  │
│                      │         │  │      └─ environment:         │  │
│                      │         │  │         production            │  │
│                      │◀──(2)── │  └─────────────────────────────┘  │
│  Receives Azure      │         │                                   │
│  access token        │         └───────────────────────────────────┘
│                      │
│  Uses token to       │         ┌───────────────────────────────────┐
│  manage resources    │ ──(3)──▶│  Azure Subscription               │
│  (ACR, Container     │         │  ├─ Resource Group                │
│   Apps, etc.)        │         │  ├─ Container Registry (ACR)      │
│                      │         │  └─ Container App                 │
└──────────────────────┘         └───────────────────────────────────┘
```

### How OIDC Federated Authentication Works

```
  GitHub Actions                GitHub OIDC Provider           Microsoft Entra ID             Azure Resources
  ─────────────                 ────────────────────           ──────────────────             ───────────────
       │                               │                              │                            │
       │  1. Request OIDC token        │                              │                            │
       │──────────────────────────────▶│                              │                            │
       │                               │                              │                            │
       │  2. Return signed JWT         │                              │                            │
       │  (contains repo, branch,      │                              │                            │
       │   environment claims)         │                              │                            │
       │◀──────────────────────────────│                              │                            │
       │                               │                              │                            │
       │  3. Present JWT to Azure      │                              │                            │
       │─────────────────────────────────────────────────────────────▶│                            │
       │                               │                              │                            │
       │                               │  4. Verify JWT signature     │                            │
       │                               │◀─────────────────────────────│                            │
       │                               │  (using OIDC discovery doc)  │                            │
       │                               │─────────────────────────────▶│                            │
       │                               │                              │                            │
       │                               │              5. Match subject claim against               │
       │                               │                 federated credentials                     │
       │                               │              ────────────────────────────                 │
       │                               │              "repo:scgiri/azure-ai-assistant              │
       │                               │               :environment:production"                    │
       │                               │               must match a credential                    │
       │                               │                              │                            │
       │  6. Return Azure access token │                              │                            │
       │◀─────────────────────────────────────────────────────────────│                            │
       │                               │                              │                            │
       │  7. Call Azure APIs (deploy, push image, etc.)               │                            │
       │────────────────────────────────────────────────────────────────────────────────────────────▶
       │                               │                              │                            │
```

> **Key point:** No client secrets are exchanged. GitHub's OIDC provider issues
> a short-lived JWT that Azure trusts because the **issuer**, **subject**, and
> **audience** are pre-registered as a Federated Identity Credential.

---

## Prerequisites

| Requirement | Details |
|---|---|
| Azure account | With an active subscription |
| Azure Portal access | [portal.azure.com](https://portal.azure.com) |
| GitHub repository | `scgiri/azure-ai-assistant` (or your fork) |
| Permissions | You must be able to create App Registrations in Microsoft Entra ID and assign roles on the subscription |

---

## Step 1 — Create the App Registration

1. Navigate to [portal.azure.com](https://portal.azure.com)
2. In the top search bar, type **Microsoft Entra ID** and select it
3. In the left sidebar, select **App registrations**
4. Click **+ New registration**

   ```
   ┌──────────────────────────────────────────────────┐
   │  Register an application                         │
   │                                                  │
   │  Name:  azure-ai-assistant-deploy                │
   │                                                  │
   │  Supported account types:                        │
   │  ● Accounts in this organizational               │
   │    directory only (Single tenant)                 │
   │                                                  │
   │  Redirect URI:  (leave blank)                    │
   │                                                  │
   │  [ Register ]                                    │
   └──────────────────────────────────────────────────┘
   ```

5. Click **Register**

### Record These Values

After registration, you land on the **Overview** page. Copy and save these:

| Field on Portal | Save As | Example |
|---|---|---|
| Application (client) ID | `AZURE_CLIENT_ID` | `e84eff28-327b-4808-a495-c23aee4447dd` |
| Directory (tenant) ID | `AZURE_TENANT_ID` | `72f988bf-86f1-41af-91ab-2d7cd011db47` |

> **Tip:** Click the copy icon next to each value to copy it to your clipboard.

---

## Step 2 — Verify the Service Principal Exists

When you create an App Registration, Azure usually creates a corresponding
**Enterprise Application** (Service Principal) automatically. Verify this:

1. In **Microsoft Entra ID**, click **Enterprise applications** in the left sidebar
2. Change the **Application type** filter to **All Applications**
3. Search for the name you used (e.g., `azure-ai-assistant-deploy`)
4. If it appears → you're good, proceed to Step 3

### If the Service Principal Is Missing

Run this command in your terminal:

```bash
az ad sp create --id <YOUR_APPLICATION_CLIENT_ID>
```

If you see *"already in use"*, the Service Principal already exists — proceed to Step 3.

---

## Step 3 — Add Federated Identity Credentials

This is the most critical step. You need **two** federated credentials to
cover both workflows in this project.

### Why Two Credentials?

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Workflow File               Trigger          Subject Claim             │
│  ─────────────               ───────          ─────────────             │
│                                                                         │
│  ci.yml                      push to main     repo:scgiri/azure-ai-    │
│  (build & push to ACR)                        assistant:ref:refs/       │
│                                               heads/main                │
│                                                                         │
│  cd-aca.yml                  push to main     repo:scgiri/azure-ai-    │
│  (deploy to Container Apps)  (env: production) assistant:environment:   │
│                                               production                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

- `ci.yml` runs on **branch `main`** (no GitHub environment) → subject uses `ref:refs/heads/main`
- `cd-aca.yml` runs on **branch `main`** with `environment: production` → subject uses `environment:production`

Azure matches the **subject** claim exactly, so each workflow needs its own credential.

### Credential A — For the CI Workflow (Branch)

1. Go to **Microsoft Entra ID** → **App registrations** → your app
2. Click **Certificates & secrets** in the left sidebar
3. Click the **Federated credentials** tab
4. Click **+ Add credential**
5. Fill in:

   | Field | Value |
   |---|---|
   | Federated credential scenario | **GitHub Actions deploying Azure resources** |
   | Organization | `scgiri` |
   | Repository | `azure-ai-assistant` |
   | Entity type | **Branch** |
   | GitHub branch name | `main` |
   | Name | `github-branch-main` |

6. Click **Add**

### Credential B — For the CD Workflow (Environment)

1. Still on the **Federated credentials** tab, click **+ Add credential** again
2. Fill in:

   | Field | Value |
   |---|---|
   | Federated credential scenario | **GitHub Actions deploying Azure resources** |
   | Organization | `scgiri` |
   | Repository | `azure-ai-assistant` |
   | Entity type | **Environment** |
   | GitHub environment name | `production` |
   | Name | `github-env-production` |

3. Click **Add**

### Verify Both Credentials

You should now see two entries:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Federated credentials (2)                                         │
│                                                                     │
│  Name                      Subject                                  │
│  ────                      ───────                                  │
│  github-branch-main        repo:scgiri/azure-ai-assistant           │
│                            :ref:refs/heads/main                     │
│                                                                     │
│  github-env-production     repo:scgiri/azure-ai-assistant           │
│                            :environment:production                   │
│                                                                     │
│  Issuer (both):            https://token.actions.githubusercontent  │
│                            .com                                     │
│  Audience (both):          api://AzureADTokenExchange               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 4 — Assign a Role on the Subscription

The App Registration now has an identity, but it has **no permissions** on
any Azure resources yet. You must assign a role.

1. In the search bar, type **Subscriptions** and select it
2. Click on your target subscription
3. Click **Access control (IAM)** in the left sidebar
4. Click **+ Add** → **Add role assignment**

### Step 4a — Choose the Role

5. In the **Role** tab, search for **Contributor**
6. Select **Contributor** and click **Next**

   ```
   ┌──────────────────────────────────────────────┐
   │  Role:  Contributor                           │
   │                                              │
   │  Description: Grants full access to manage   │
   │  all resources, but does not allow you to    │
   │  assign roles in Azure RBAC.                 │
   │                                              │
   │  [ Next ]                                    │
   └──────────────────────────────────────────────┘
   ```

### Step 4b — Select Members

7. Under **Assign access to**, select **User, group, or service principal**
8. Click **+ Select members**
9. In the search box on the right panel, type your app name (e.g., `azure-ai-assistant-deploy`)

   > **Troubleshooting:** If it doesn't appear:
   > - Wait 2-5 minutes after creating the App Registration
   > - Try searching by **Application (client) ID** instead of name
   > - Verify the Service Principal exists (see Step 2)

10. Click on your app to select it
11. Click **Select**
12. Click **Review + assign** → **Review + assign** again

### Verify the Role Assignment

Still on **Access control (IAM)**:

1. Click the **Role assignments** tab
2. Search for your app name
3. You should see:

   ```
   ┌────────────────────────────────────────────────────────────┐
   │  Name                           Role          Scope       │
   │  ────                           ────          ─────       │
   │  azure-ai-assistant-deploy      Contributor   Subscription│
   └────────────────────────────────────────────────────────────┘
   ```

---

## Step 5 — Get the Subscription ID

1. Go to **Subscriptions** in the portal
2. Click on your subscription
3. On the **Overview** page, copy the **Subscription ID**
4. Save it as `AZURE_SUBSCRIPTION_ID`

---

## Step 6 — Create the GitHub Environment

The CD workflow (`cd-aca.yml`) uses `environment: production`. This
environment must exist in your GitHub repository.

1. Go to your GitHub repo → **Settings** → **Environments**
2. If `production` does not exist, click **New environment**
3. Name it exactly: `production`
4. Click **Configure environment**
5. (Optional) Add protection rules like required reviewers

---

## Step 7 — Add Secrets to GitHub

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each of the following:

| Secret Name | Value | Where You Got It |
|---|---|---|
| `AZURE_CLIENT_ID` | Application (client) ID | Step 1 — App Registration Overview |
| `AZURE_TENANT_ID` | Directory (tenant) ID | Step 1 — App Registration Overview |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | Step 5 — Subscription Overview |

### Additional Secrets for Deployment

These are required by `cd-aca.yml` but are **not** related to App Registration:

| Secret Name | Description |
|---|---|
| `RESOURCE_GROUP` | Azure Resource Group name |
| `CONTAINER_APP_NAME` | Container App name |
| `CONTAINERAPPS_ENVIRONMENT` | Container Apps Environment name |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment/model name |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version |

---

## Summary — What You Created

```
Microsoft Entra ID
└── App Registration: azure-ai-assistant-deploy
    ├── Application (client) ID  ──▶  AZURE_CLIENT_ID
    ├── Directory (tenant) ID    ──▶  AZURE_TENANT_ID
    ├── Federated Credentials
    │   ├── github-branch-main         (for ci.yml)
    │   └── github-env-production      (for cd-aca.yml)
    └── Service Principal
        └── Role: Contributor on Subscription ──▶ AZURE_SUBSCRIPTION_ID

GitHub Repository
├── Settings / Environments / production
└── Settings / Secrets
    ├── AZURE_CLIENT_ID
    ├── AZURE_TENANT_ID
    └── AZURE_SUBSCRIPTION_ID
```

---

## Troubleshooting

### Error: "No subscriptions found"

**Cause:** The Service Principal has no role assignment on any subscription.

**Fix:** Complete Step 4 — Assign a Role on the Subscription.

---

### Error: "No matching federated identity record found for presented assertion subject"

**Cause:** The subject claim in the OIDC token does not match any Federated
Identity Credential.

**Fix:** Check the error message for the exact subject string and compare it
against your credentials in Step 3.

Common mismatches:

| Workflow Uses | Expected Subject | Required Entity Type |
|---|---|---|
| `environment: production` | `repo:ORG/REPO:environment:production` | **Environment** |
| branch `main` (no environment) | `repo:ORG/REPO:ref:refs/heads/main` | **Branch** |
| pull request | `repo:ORG/REPO:pull_request` | **Pull request** |
| tag `v1.0` | `repo:ORG/REPO:ref:refs/tags/v1.0` | **Tag** |

---

### Error: "The service principal name ... is already in use"

**Cause:** The Service Principal already exists. This is not actually an error.

**Fix:** No action needed. Proceed with role assignment (Step 4).

---

### Service Principal Not Appearing in IAM Members List

**Possible causes and fixes:**

1. **Propagation delay** — Wait 2-5 minutes after creating the App Registration
2. **Not searching** — You must type the name in the search box; it doesn't appear in a browse list
3. **Search by Client ID** — Try pasting the Application (client) ID instead of the name
4. **Service Principal missing** — Check Enterprise Applications (Step 2)

---

### Error: "AADSTS700024: Client assertion is not within its valid time range"

**Cause:** Clock skew between GitHub Actions runner and Azure.

**Fix:** This is transient. Re-run the workflow. If persistent, check that your
federated credential's issuer URL is exactly:
```
https://token.actions.githubusercontent.com
```

---

## Security Best Practices

- **Never use client secrets** for GitHub Actions — use federated credentials (OIDC) instead
- **Never paste secrets in chat, email, or commits** — if exposed, rotate immediately
- **Use least-privilege roles** — for production, consider scoping the role to a specific Resource Group instead of the entire Subscription:
  ```
  Scope: /subscriptions/<SUB_ID>/resourceGroups/<RG_NAME>
  ```
- **Set expiry on credentials** — if you do use client secrets for other purposes, set short expiry periods
- **Review role assignments periodically** — remove unused service principals
