# Laws Markdown Schema

## Frontmatter

- `id`: law identifier
- `name`: law name
- `type`: law type
- `department`: responsible department
- `date_promulgated`: promulgation date (`YYYY-MM-DD`)
- `date_enforced`: enforcement date (`YYYY-MM-DD`)
- `articles_count`: number of articles

## Body

Each article is rendered as a Markdown section:

```md
## 제1조 목적
법 조문 텍스트...
```

Optional article clauses can be emitted as bullet points under the article section.

## Example

See `sample-law.md`.
