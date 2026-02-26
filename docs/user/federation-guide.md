# Federation Guide

Federation allows you to share proteins with other mesh instances and subscribe to proteins from other users.

## How It Works

1. **Tag proteins as public**: Add `#public` tag to any protein you want to share
2. **GitHub sync**: Public proteins sync to your `eidolon-proteins` repository
3. **Subscribe**: Other users can subscribe to your repo to import your proteins
4. **Reciprocal**: You can subscribe to other users' protein repos

## Setup

### 1. Create a GitHub Personal Access Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a name (e.g., "Eidolon Mesh")
4. Select scopes:
   - ✅ `repo` (full control of private repositories)
   - ✅ `public_repo` (access to public repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### 2. Configure in Eidolon Mesh

1. Open **Settings**
2. Paste your GitHub token
3. (Optional) Enter an **Organization Name** if using an org
4. Click **"Save & Close"**

The mesh will perform "Mitosis" and automatically create:
- **`eidolon-nucleus`** (Private)
- **`eidolon-proteins`** (Public)

## Sharing Proteins

### Tag Proteins as Public

When creating or editing a protein, add the `#public` tag:

```
Tags: #public #knowledge #philosophy
```

### Privacy Control (Ingestion)

When ingesting files (drag & drop), use the **Privacy Toggle** in the Ingestion Panel:
- **🔒 Private (Default)**: Forces all generated proteins to be private (Nucleus only), overriding any AI suggestions.
- **🤖 Auto**: Lets the AI decide whether to tag as `#public` or `#private` based on content.
- **🌍 Public**: Forces all generated proteins to be tagged `#public` (synced to Cytoplasm).

### Syncing with Nucleus

Your data lives in your private Nucleus repository. To sync across devices:

1. Go to **🕸️ Network** tab
2. Click the **`↻` Sync** button
3. This pulls the latest state from your Nucleus repo

## Subscribing to Other Meshes

### 1. Find a Mesh to Subscribe To

Look for users who have shared their `eidolon-proteins` repository. Example:

```
github.com/meshseed/eidolon-proteins
```

### 2. Subscribe

1. Go to **🕸️ Network** tab
2. Enter the GitHub username in the **"Subscribe"** field
3. Click **"Add Subscription"**

### 3. Import Proteins

1. The mesh will fetch proteins from the subscribed repo
2. Review the proteins in the list
3. Click **"Import"** on proteins you want to add to your connectome
4. Imported proteins will appear in your vault and graph

## Privacy

- **Only proteins tagged `#public` are shared**
- **Private proteins stay local** (never leave your browser)
- **You control what you share** (tag-based opt-in)
- **Subscriptions are one-way** (subscribing to someone doesn't give them access to your proteins)

## Best Practices

### Curate Your Public Proteins

- Only share high-quality, well-formed proteins
- Use descriptive titles and summaries
- Add relevant tags for discoverability
- Review before tagging as `#public`

### Respect Attribution

- If you import someone's protein, consider citing the source
- Add a tag like `#from:username` to track provenance

### Contribute to the Mesh

- Share valuable insights and knowledge
- Help build the collective connectome
- Participate in the distributed organism

## Troubleshooting

### "GitHub Auth Failed"

- Check that your token has the correct scopes (`repo`)
- Make sure the token hasn't expired
- Try regenerating a new token

### "Repository Not Found"

- Verify the username is correct
- Check that the user has a public `eidolon-proteins` repo
- Make sure the repo isn't empty

### Proteins Not Syncing

- Check that proteins are tagged `#public`
- Verify your GitHub token is configured
- Check GitHub rate limits (60 requests/hour for unauthenticated, 5000/hour for authenticated)

## Example Workflow

1. **Create a protein** from a conversation or document
2. **Review and refine** the protein in the vault
3. **Tag as `#public`** if you want to share it
4. **Protein syncs** to your GitHub repo automatically
5. **Others subscribe** to your repo
6. **They import** your proteins into their mesh
7. **Knowledge propagates** across the distributed organism

## Community Repos

### Official Seed Data

- **meshseed/eidolon-proteins**: Golden Connectome starter proteins

### Community Contributors

*Add your repo here via pull request!*

---

**Questions?** Open an issue on [GitHub](https://github.com/meshseed/eidolon-public/issues)

**Live App:** [eidolon-mesh.net](https://eidolon-mesh.net)
