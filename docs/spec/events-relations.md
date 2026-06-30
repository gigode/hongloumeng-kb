# 事件与关系规范

首版事件和关系只覆盖前五回的骨架，用来支撑图谱浏览。

## 事件

事件字段：

- `id`
- `name`
- `type`
- `chapter`
- `paragraphs`
- `participants`
- `objects`
- `places`
- `summary`

事件类型先使用自由字符串，如 `dream_frame`、`arrival`、`case_judgment`、`family_introduction`。

## 关系

首版关系类型：

- `family_parent_child`
- `family_spouse`
- `family_sibling`
- `kinship_cousin`
- `household_member`
- `serves`
- `resides_at`
- `owns_or_carries`
- `appears_in_event`
- `co_occurs`

每条关系必须有证据：

```json
{
  "chapter": "003",
  "paragraph": "12",
  "quote": "林黛玉进荣国府拜见贾母"
}
```

证据不充分时将 `confidence` 设为 `medium` 或 `low`。
