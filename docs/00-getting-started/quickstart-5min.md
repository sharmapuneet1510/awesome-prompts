# ⚡ 5-Minute Quick Start

Get productive with awesome-prompts in 5 minutes.

## Install (1 min)

```bash
pip install awesome-prompts
```

Done. You have everything you need.

## Try Archify (2 min)

Create a diagram in 30 seconds:

```bash
cat > my-diagram.json << 'EOF'
{
  "type": "architecture",
  "version": "1.0.0",
  "title": "My First Diagram",
  "nodes": [
    { "id": "web", "label": "Frontend", "color": "frontend" },
    { "id": "api", "label": "Backend", "color": "backend" },
    { "id": "db", "label": "Database", "color": "database" }
  ],
  "edges": [
    { "id": "e1", "from": "web", "to": "api", "label": "API calls" },
    { "id": "e2", "from": "api", "to": "db", "label": "Queries" }
  ]
}
EOF
```

Validate it:

```bash
cat my-diagram.json | python3 -m archify.bin.archify validate
```

See the output:
```
✓ Validation passed
  Nodes: 3
  Edges: 2
```

## Use in Your Project (2 min)

Export prompts to your project:

```bash
# List what's available
python3 -m tools.exporter --list

# Export to your project
python3 -m tools.exporter --target claude --target-project ~/path/to/your-project
```

Now open your project in Claude Code or Cursor — you'll see all the skills, prompts, and agents available.

## Next Steps

- **Read the guides**: [docs/01-workflows/](../01-workflows/) for use cases
- **Learn the concepts**: [docs/00-getting-started/concepts.md](concepts.md)
- **Full documentation**: [README.md](../../README.md)
- **Contribute**: [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

## That's It! 🎉

You now have:
- ✅ A working diagram system
- ✅ Prompts and skills for your project
- ✅ A foundation for spec-driven development

Questions? See [README.md](../../README.md) or start a [discussion](https://github.com/sharmapuneet1510/awesome-prompts/discussions).
