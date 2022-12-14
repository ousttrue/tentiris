# 実装

## validate

* 内部リンクのチェック

## formatter

### mdformat
<https://mdformat.readthedocs.io/en/stable/>

`pip install mdformat-myst`

## completion

### 内部リンクの対象を列挙したい

```
{doc}`ここ<参照先のパス>` を確認ください
{doc}`参照先のパス` を確認ください
```

### toctree の対象を列挙したい
````
```{toctree}
vscode_extension/index
pygls/index
markdown/index
```
````

### 内部リンクにジャンプしたい

- goto-definition

## ページのアウトライン表示

VSCode 標準で十分かも？

## semantic token

VSCode 標準で十分かも？
