# Google Cloud Console Setup

## 1. Create a New Project

- Log in to [Google Cloud Console](https://console.cloud.google.com)
- Select **New Project**
- Enter project details and create

---

## 2. Configure OAuth Consent Screen

- Search for **APIs and Services**
- Go to **OAuth Consent Screen** → **Get Started**
- Complete the following:
  - **App name** and **Support email**
  - **User type**: External or Internal (Organization)
  - **Developer contact email**
- Click **Save and Continue** → **Finish** → **Create**

---

## 3. Create OAuth Credentials

- Search for **APIs and Services**
- Go to **Credentials**
- Click **+ Create Credentials** → **OAuth client ID**
- Configure:
  - **Application type**: Web application
  - **Name**: (your client name)
  - **Authorized JavaScript origins**: `http://localhost:8026`
  - **Authorized redirect URIs**: `http://localhost:8026/auth/callback`
- Click **Create**
- Download the JSON file and save credentials
- Click **OK**
