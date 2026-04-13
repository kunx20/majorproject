# Upload Project to GitHub - Step-by-Step Guide

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Log in to your account
3. Click the **"+"** icon in the top-right corner
4. Select **"New repository"**
5. Fill in the details:
   - **Repository name**: `clinical-guideline-QA`
   - **Description**: A FastAPI-based clinical guideline Q&A system with hybrid retrieval and safety checks
   - **Visibility**: Choose **Public** or **Private**
   - **Initialize repository**: Leave unchecked (we already have commits)
6. Click **"Create repository"**

## Step 2: Add Remote and Push Code

After creating the repository, GitHub will show you the push commands. Run these in your terminal:

```bash
cd C:\Users\HP\Desktop\clinical_guideline_QA

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/clinical-guideline-QA.git

# Rename branch to main (if not already)
git branch -M main

# Push all commits to GitHub
git push -u origin main
```

## Step 3: Verify on GitHub

1. Go to your new repository URL: `https://github.com/YOUR_USERNAME/clinical-guideline-QA`
2. You should see:
   - ✅ All your source code
   - ✅ Updated README with full documentation
   - ✅ .gitignore excluding cache files
   - ✅ .env.example for configuration
   - ✅ Git commit history (6 commits)

## Step 4: Add GitHub Topics (Optional)

1. Go to your repository settings
2. Under "About", add topics:
   - `fastapi`
   - `clinical`
   - `qa-system`
   - `hybrid-search`
   - `python`

## Step 5: Enable GitHub Pages (Optional)

To host the frontend on GitHub Pages:

1. Go to Settings → Pages
2. Select source: `main` branch, `/docs` folder
3. Your frontend will be at: `https://YOUR_USERNAME.github.io/clinical-guideline-QA/`

## Step 6: Share Your Repository

Your project is now on GitHub! Share the link:
- Repository: `https://github.com/YOUR_USERNAME/clinical-guideline-QA`
- Clone command: `git clone https://github.com/YOUR_USERNAME/clinical-guideline-QA.git`

## For Future Updates

After making changes locally:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

## Troubleshooting

### Authentication Issues
If you get authentication errors, use a personal access token:
```bash
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/clinical-guideline-QA.git
```

Or configure SSH:
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/clinical-guideline-QA.git
```

### Already Have Remote?
If you already added a remote, update it:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/clinical-guideline-QA.git
```

---

**Your project is ready to push! All tests pass ✅ and documentation is complete 📚**
