# Sync Figma branches to Github issue

Sync open Figma branches into a GitHub issue.

## Inputs

| Input          | Descripción                          |
| -------------- | ------------------------------------ |
| `figma-token`  | Token de acceso a la API de Figma.   |
| `github-token` | Token de GitHub para repos privados. |
| `project-id`   | Sync all files inside project        |

## Ejemplo de uso

```yaml
name: Sync branches daily
on:
  schedule:
    - cron: "0 8 * * *"
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: yceballost/figma-branches-status@v1
        with:
          figma-token: ${{ secrets.FIGMA_TOKEN }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          project-ids: "12345678,87654321"
```
