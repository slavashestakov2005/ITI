
# Система работы Пайплайна
Пайплайн состит из блоков, блоки же обрабатывают обьекты

```mermaid
flowchart TD

    A1[Ввод] -->|Объект| B
    A2[Ввод] -->|Объект| B
    A3[Ввод] -->|Объект| B

    B[Блок] --> |Объект|C

    B1[Ввод] -->|Объект| C

    C[Блок] -->|Объект| D
    D[Вывод]
```

## Пример

<table>
<tr>
<td valign="top">

**Математика**
| student | res |
|---------|-----|
| 1       | 5   |
| 2       | 27  |
| 123     | 10  |

</td>
<td valign="top">

**Школьники**
| id   | name  |
|------|-------|
| 1    | Slava |
| 2    | Dima  |
| 3    | Dan   |

</td>
<td valign="top">

**Декодированное**
| name  | score |
|-------|-------|
| Slava | 5     |
| Dima  | 27    |

</td>
</tr>
</table>

```mermaid
graph TD
    A[math]:::source
    B[students]:::source
    C[decode_math]:::process
    D[Выход]:::output

    A -->|Математика| C
    B -->|Школьники| C
    C -->|Декодированное| D

    classDef source fill:#bbdefb,stroke:#1976d2,stroke-width:2px;
    classDef process fill:#fff9c4,stroke:#ffa000,stroke-width:2px;
    classDef output fill:#c8e6c9,stroke:#388e3c,stroke-width:2px;
```

<details>
<summary>Yaml описание</summary>

```yaml
math:
  type: db_read
  callback: in_test_read_math
  output:
    type: table
    columns:
      student: int
      res: int
students:
  type: db_read
  callback: in_test_read_students
  output:
    type: table
    columns:
      id: int
      name: str
decode_math:
  type: agg
  callback: in_test_decode_math
  input:
    - math
    - students
  output:
    type: table
    columns:
      name: str
      score: int
```
</details>
