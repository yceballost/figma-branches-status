# Sync Figma branches to Github issue

Sync open Figma branches into a GitHub issue with Github Actions.

In [Mística Design System](https://brandfactory.telefonica.com/mistica) we use this workflow to have a control about all the branches opened in important files of the system.

You can see our usage [here](https://github.com/Telefonica/mistica-design/issues/1927)

The table is composed by 5 columns

1. File name
2. Branch name
3. Issue related
4. Status (from Github project)
5. Last modification

We follow a simple nomenclature to name branches:  
`#0000 - Issue name`

With this nomenclature in Figma branches you can sync figma branches with Github issues automatically

## Inputs

| Input          | Descripción                          |
| -------------- | ------------------------------------ |
| `figma-token`  | Token de acceso a la API de Figma.   |
| `github-token` | Token de GitHub para repos privados. |
| `project-id`   | Sync all files inside project        |

### How to get project-id from Figma projects

Copy link from a project in Figma and use the number after `project/` and use it in project-id field in the action. (check usage example section)

For example: `https://www.figma.com/files/1556734703143062955/project/12345678`

## Usage example

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
