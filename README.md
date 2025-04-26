# Sync Figma branches to Github issue

Sync open Figma branches into a GitHub issue with Github Actions.

In [Mística Design System](https://brandfactory.telefonica.com/mistica) we use this workflow to have a control about all the branches opened in important files of the system.

You can see our usage [here](https://github.com/Telefonica/mistica-design/issues/1927)

The table is composed by 5 columns

| File Name | Branch Names                                        | Issue | Status      | Last Modification |
| :-------- | :-------------------------------------------------- | :---- | :---------- | :---------------- |
| Filename  | [#1234 - Figma branch name ](https://www.figma.com) | #1234 | In progress | 1 d               |

We follow a simple nomenclature to name branches:  
`#0000 - Issue name`

Including the issue number with # (#1234) in Figma branch name you can sync figma branches with Github issues automatically

## Inputs

| Input          | Descripción                                   |          |
| -------------- | --------------------------------------------- | -------- |
| `figma-token`  | Token de acceso a la API de Figma.            | required |
| `github-token` | Token de GitHub para repos privados.          | required |
| `project-id`   | Sync all files inside project                 | required |
| `issue-number` | Choose the issue number where print the table | required |

You must have created an issue in your repo to print the table on it.

### How to get project-id from Figma projects

Copy link from a project in Figma and use the number after `project/` and use it in project-id field in the action. (check usage example section)

For example: `https://www.figma.com/files/1556734703143062955/project/12345678`

## Usage example

```yaml
name: Figma branches status
on:
  workflow_dispatch:
  schedule:
    - cron: "0 8 * * *"
jobs:
  sync-figma-branches:
    runs-on: ubuntu-latest
    steps:
      - uses: yceballost/figma-branches-status@v1
        with:
          figma-token: ${{ secrets.FIGMA_TOKEN }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          project-ids: "12345678,87654321"
          issue-number: "1"
```
