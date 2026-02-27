# Cura3.ai — Azure Deployment Guide
# ════════════════════════════════════════════════════════
# Step-by-step guide to deploy the full Cura3.ai platform
# to Microsoft Azure.
# ════════════════════════════════════════════════════════

## Prerequisites

Before starting, ensure you have:

1. **Azure Account** — [Create a free account](https://azure.microsoft.com/free/) if you don't have one
2. **Azure CLI** — Install from [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
   ```powershell
   winget install Microsoft.AzureCLI
   ```
3. **GitHub Repository** — Your code pushed to a GitHub repository
4. **MongoDB Atlas Cluster** — Already set up at [MongoDB Atlas](https://www.mongodb.com/atlas)

---

## Step 1: Install Azure CLI & Login

```powershell
# Install Azure CLI (if not already installed)
winget install Microsoft.AzureCLI

# Login to your Azure account
az login

# Verify your subscription
az account show --query "{name:name, id:id}" -o table
```

---

## Step 2: Create Azure Resource Group

```powershell
# Create a resource group (choose a region close to your users)
az group create --name cura3ai-rg --location centralindia
```

---

## Step 3: Deploy Backend (Azure App Service — Python)

```powershell
# Create an App Service Plan (B1 for small apps, S1 for production)
az appservice plan create \
  --name cura3ai-backend-plan \
  --resource-group cura3ai-rg \
  --sku B1 \
  --is-linux

# Create the Web App for the Python backend
az webapp create \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --plan cura3ai-backend-plan \
  --runtime "PYTHON:3.12"

# Configure environment variables
az webapp config appsettings set \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --settings \
    MONGODB_URI="your-mongodb-atlas-connection-string" \
    MONGODB_DB_NAME="cura3ai" \
    OPENAI_API_KEY="your-openai-api-key" \
    GOOGLE_CLIENT_ID="your-google-client-id" \
    GOOGLE_CLIENT_SECRET="your-google-client-secret" \
    OAUTH_REDIRECT_URI="https://cura3ai-backend.azurewebsites.net/api/v1/auth/callback" \
    JWT_SECRET_KEY="$(openssl rand -hex 32)" \
    FRONTEND_URL="https://cura3ai-frontend.azurewebsites.net" \
    APPINSIGHTS_CONNECTION_STRING="" \
    WEBSITES_PORT=8000

# Configure startup command
az webapp config set \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --startup-file "uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Enable HTTPS only
az webapp update \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --https-only true

# Deploy using local Git or zip deploy
cd backend
az webapp up \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --runtime "PYTHON:3.12"
```

### Verify Backend Deployment
```powershell
curl https://cura3ai-backend.azurewebsites.net/health
# Expected: {"status":"healthy","database":"connected",...}
```

---

## Step 4: Deploy Frontend (Azure Static Web Apps)

### Option A: Azure Static Web Apps (Recommended for Next.js)

```powershell
# Create a Static Web App (linked to your GitHub repo)
az staticwebapp create \
  --name cura3ai-frontend \
  --resource-group cura3ai-rg \
  --source https://github.com/YOUR_USERNAME/AI-Agents-for-Medical-Diagnostics \
  --location centralindia \
  --branch main \
  --app-location "/frontend" \
  --output-location ".next" \
  --login-with-github
```

### Option B: Azure App Service (if Static Web Apps doesn't work)

```powershell
# Create App Service for frontend
az webapp create \
  --name cura3ai-frontend \
  --resource-group cura3ai-rg \
  --plan cura3ai-backend-plan \
  --runtime "NODE:22-lts"

# Set environment variables
az webapp config appsettings set \
  --name cura3ai-frontend \
  --resource-group cura3ai-rg \
  --settings \
    NEXT_PUBLIC_API_URL="https://cura3ai-backend.azurewebsites.net"

# Deploy
cd frontend
az webapp up \
  --name cura3ai-frontend \
  --resource-group cura3ai-rg
```

---

## Step 5: MongoDB Atlas Configuration

1. Go to [MongoDB Atlas Dashboard](https://cloud.mongodb.com)
2. Click **Network Access** → **Add IP Address**
3. Add the Azure backend's outbound IPs:
   ```powershell
   az webapp show --name cura3ai-backend --resource-group cura3ai-rg \
     --query "outboundIpAddresses" -o tsv
   ```
4. Add each IP to the Atlas whitelist
5. Alternatively, select **Allow Access from Anywhere** (0.0.0.0/0) for simplicity

---

## Step 6: Configure Google OAuth URLs

Update your Google Cloud Console OAuth settings:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client ID
3. Add **Authorized redirect URIs**:
   - `https://cura3ai-backend.azurewebsites.net/api/v1/auth/callback`
4. Add **Authorized JavaScript origins**:
   - `https://cura3ai-frontend.azurewebsites.net`
5. Save

---

## Step 7: Set Up GitHub Actions Secrets

In your GitHub repository, go to **Settings → Secrets → Actions** and add:

| Secret Name | Where to Get It |
|-------------|----------------|
| `AZURE_CREDENTIALS` | `az ad sp create-for-rbac --name cura3ai-deploy --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/cura3ai-rg --sdk-auth` |
| `AZURE_BACKEND_APP_NAME` | `cura3ai-backend` |
| `AZURE_STATIC_WEB_APPS_TOKEN` | Azure Portal → Static Web App → Manage deployment token |
| `AZURE_FRONTEND_URL` | `https://cura3ai-frontend.azurewebsites.net` |

---

## Step 8: Enable Application Insights (Optional)

```powershell
# Create Application Insights resource
az monitor app-insights component create \
  --app cura3ai-insights \
  --location centralindia \
  --resource-group cura3ai-rg \
  --application-type web

# Get the connection string
az monitor app-insights component show \
  --app cura3ai-insights \
  --resource-group cura3ai-rg \
  --query "connectionString" -o tsv

# Set it as an environment variable on the backend
az webapp config appsettings set \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --settings APPINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
```

---

## Step 9: Custom Domain (Optional)

```powershell
# Add custom domain to backend
az webapp config hostname add \
  --webapp-name cura3ai-backend \
  --resource-group cura3ai-rg \
  --hostname api.cura3.ai

# Add free managed SSL certificate
az webapp config ssl create \
  --name cura3ai-backend \
  --resource-group cura3ai-rg \
  --hostname api.cura3.ai

# Add custom domain to frontend (Static Web Apps)
az staticwebapp hostname set \
  --name cura3ai-frontend \
  --resource-group cura3ai-rg \
  --hostname cura3.ai
```

**DNS Configuration:**
- Add a CNAME record pointing `api.cura3.ai` → `cura3ai-backend.azurewebsites.net`
- Add a CNAME record pointing `cura3.ai` → your Static Web App default hostname

---

## Step 10: Post-Deployment Checklist

- [ ] Backend health check returns 200: `https://cura3ai-backend.azurewebsites.net/health`
- [ ] Frontend loads: `https://cura3ai-frontend.azurewebsites.net`
- [ ] Google OAuth login works end-to-end
- [ ] Report upload and diagnosis flow works
- [ ] Chat follow-up works
- [ ] Admin panel accessible for admin users
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] PDF download works
- [ ] Cookie consent banner appears
- [ ] Rate limiting active
- [ ] Application Insights receiving telemetry (if configured)

---

## Estimated Azure Costs (Monthly)

| Resource | SKU | Est. Cost |
|----------|-----|-----------|
| App Service (Backend) | B1 | ~$13/month |
| Static Web Apps (Frontend) | Free | $0/month |
| MongoDB Atlas | M0 (Free) | $0/month |
| Application Insights | Free tier | $0/month |
| **Total** | | **~$13/month** |

> For production with more users, upgrade to S1 ($73/month) and M10 Atlas ($57/month).

---

## Troubleshooting

### Backend won't start
```powershell
# Check logs
az webapp log tail --name cura3ai-backend --resource-group cura3ai-rg
```

### OAuth redirect fails
- Verify `OAUTH_REDIRECT_URI` env var matches Google Console settings
- Verify `FRONTEND_URL` env var matches actual frontend URL

### Database connection fails
- Check MongoDB Atlas Network Access whitelist
- Verify `MONGODB_URI` includes proper credentials and database name

### CORS errors
- Verify `FRONTEND_URL` in backend env vars matches the actual frontend origin
- Check browser console for specific CORS error messages
