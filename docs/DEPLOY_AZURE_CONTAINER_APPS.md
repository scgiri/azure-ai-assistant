# Deploy to Azure Container Apps (GitHub Actions CD)

This guide sets up continuous deployment from GitHub to Azure Container Apps.

## 1) Azure resources required

Create or reuse:
- Azure Resource Group
- Azure Container Apps Environment
- Azure Container App
- Azure Container Registry (ACR)

## 2) Configure GitHub OIDC auth to Azure

Use a Microsoft Entra application/service principal and add a federated credential for your GitHub repo.

High-level steps:
1. Create app registration + service principal.
2. Grant it access to your resource group (Contributor is common for demos).
3. Add a federated credential for your repo and branch (`main`).
4. Copy values for:
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`

## 3) Add GitHub repository secrets

Go to GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

Required secrets for `.github/workflows/cd-aca.yml`:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ACR_LOGIN_SERVER` (example: `myregistry.azurecr.io`)
- `ACR_USERNAME`
- `ACR_PASSWORD`
- `RESOURCE_GROUP`
- `CONTAINER_APP_NAME`
- `CONTAINERAPPS_ENVIRONMENT`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

## 4) Trigger deployment

Two options:
- Push to `main` (workflow auto-runs for app changes)
- Run manually from GitHub Actions tab (`workflow_dispatch`)

Workflow file:
- `.github/workflows/cd-aca.yml`

## 5) Verify deployment

- Open Azure Portal → Container App → Revisions/Logs
- Confirm latest image tag deployed
- Test endpoint:
  - `GET /health`
  - `POST /assist`

## Notes

- For production, prefer managed identity + Key Vault references instead of plain secrets for runtime configuration.
- Restrict role assignments to least privilege once your demo phase is complete.
