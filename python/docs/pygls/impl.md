# 実装

## validate

* 内部リンクのチェック

## formatter

### mdformat
<https://mdformat.readthedocs.io/en/stable/>

`pip install mdformat-myst`

## completion

### 内部リンクを列挙したい

```
[ここ](参照先のパス)を確認ください
{doc}`ここ<参照先のパス>` を確認ください
{doc}`参照先のパス` を確認ください
```

### toctree を列挙したい
````
```{toctree}
vscode_extension/index
pygls/index
markdown/index
```
````

### myst のディレクティブを列挙したい

````
```{block_directive}
```

{inline_directive}`hoge`
````

### block_directive の引数

````
```{block_directive}
:maxdepth: 2
:caption: Content
:param1: some
:param2: fuga
```
````

## goto-definition
### 内部リンクにジャンプしたい

## ページのアウトライン表示

VSCode 標準で十分かも？

## semantic token

VSCode 標準で十分かも？
