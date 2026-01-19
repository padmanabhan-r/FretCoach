# FretCoach Documentation

This directory contains the complete documentation for FretCoach, published as GitHub Pages.

## 📚 Documentation Structure

### Getting Started
- **[index.md](index.md)** - Main landing page and navigation hub
- **[introduction.md](introduction.md)** - Why FretCoach exists and how it works
- **[quickstart.md](quickstart.md)** - Get up and running in 5 minutes
- **[judges-start-here.md](judges-start-here.md)** - Essential guide for Comet Opik hackathon reviewers

### System Components
- **[desktop-app.md](desktop-app.md)** - Desktop application deep dive
- **[web-dashboard.md](web-dashboard.md)** - Web analytics platform (coming soon)
- **[portable-device.md](portable-device.md)** - Raspberry Pi edge device (coming soon)

### Architecture & Technical
- **[architecture.md](architecture.md)** - Overall system design and component interaction
- **[ai-coaching.md](ai-coaching.md)** - LLM-powered adaptive coaching system
- **[audio-engine.md](audio-engine.md)** - Real-time DSP and metric calculation (coming soon)
- **[database.md](database.md)** - PostgreSQL schema and data flow (coming soon)

### Reference
- **[appendix-audio-math.md](appendix-audio-math.md)** - Deep dive into DSP formulas and algorithms
- **[api-reference.md](api-reference.md)** - FastAPI endpoints (coming soon)
- **[configuration.md](configuration.md)** - Environment setup guide (coming soon)

## 🚀 Publishing to GitHub Pages

### Initial Setup

1. **Enable GitHub Pages in repository settings:**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` or `master`
   - Folder: `/docs`
   - Save

2. **Wait for deployment** (usually 1-2 minutes)

3. **Access at:** `https://yourusername.github.io/FretCoach/`

### Updating Documentation

Simply commit and push changes to any `.md` file in this directory. GitHub Actions will automatically rebuild and deploy.

```bash
# Edit documentation
vim docs/introduction.md

# Commit and push
git add docs/
git commit -m "Update documentation"
git push origin main

# GitHub Pages will automatically rebuild in 1-2 minutes
```

## 🎨 Styling

The documentation uses the **Cayman theme** configured in `_config.yml`.

### Custom Styling (Optional)

To customize appearance, create `assets/css/style.scss`:

```scss
---
---

@import "{{ site.theme }}";

// Custom CSS here
```

## 📝 Writing Guidelines

### Markdown Features

**Internal links:**
```markdown
[Quickstart Guide](quickstart.md)
[Desktop App](desktop-app.md)
```

**External links:**
```markdown
[Live Demo](https://fretcoach.online)
[Opik Project](https://comet.com/opik/...)
```

**Code blocks:**
```markdown
```python
def example():
    pass
`` `
```

**Math (KaTeX):**
```markdown
Inline: $E = mc^2$

Block:
$$
f(x) = \int_{-\infty}^{\infty} e^{-x^2} dx
$$
```

**Tables:**
```markdown
| Metric | Description |
|--------|-------------|
| Pitch  | Accuracy    |
| Timing | Stability   |
```

### Style Guidelines

1. **Clear headings** - Use hierarchical structure (H1 → H2 → H3)
2. **Short paragraphs** - 2-4 sentences maximum
3. **Code examples** - Include practical, runnable code
4. **Diagrams** - Use ASCII art for simple architecture diagrams
5. **Concise** - No fluff, get to the point

### Navigation

Each page should have navigation links at the bottom:

```markdown
---

**Navigation:**
- [← Previous Page](previous.md)
- [Next Page →](next.md)
- [Back to Index](index.md)
```

## 🔍 Testing Locally

### With Jekyll (Recommended)

```bash
# Install Jekyll (macOS)
brew install ruby
gem install bundler jekyll

# Navigate to docs
cd docs

# Create Gemfile
cat > Gemfile << 'EOF'
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "webrick"
EOF

# Install dependencies
bundle install

# Serve locally
bundle exec jekyll serve

# Visit http://localhost:4000
```

### With Python (Simple)

```bash
# Navigate to docs
cd docs

# Serve with Python
python3 -m http.server 8000

# Visit http://localhost:8000
# Note: This won't render Jekyll templates, just raw markdown
```

## 📊 Documentation Status

| Document | Status | Progress |
|----------|--------|----------|
| index.md | ✅ Complete | 100% |
| introduction.md | ✅ Complete | 100% |
| quickstart.md | ✅ Complete | 100% |
| judges-start-here.md | ✅ Complete | 100% |
| desktop-app.md | ✅ Complete | 100% |
| architecture.md | ✅ Complete | 100% |
| ai-coaching.md | ✅ Complete | 100% |
| appendix-audio-math.md | ✅ Complete | 100% |
| web-dashboard.md | 🚧 In Progress | 60% |
| portable-device.md | 🚧 In Progress | 40% |
| audio-engine.md | 🚧 In Progress | 50% |
| database.md | 📝 Planned | 0% |
| api-reference.md | 📝 Planned | 0% |
| configuration.md | 📝 Planned | 0% |

## 🎯 For Hackathon Judges

If you're reviewing this project for the Comet Opik hackathon:

→ **Start here:** [judges-start-here.md](judges-start-here.md)

This guide provides:
- Quick demo walkthrough
- Opik integration highlights
- Key evaluation points
- Direct links to trace data

## 📞 Contact

Questions or issues with the documentation?
- Open an issue in the GitHub repository
- Check [fretcoach.online](https://fretcoach.online) for live demos

---

**Last Updated:** January 2026
