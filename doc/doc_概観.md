# 概観

ものを動かす範囲まで実装した。

## モジュールの説明

### 依存関係

依存関係は以下の通り。

```Mermaid
graph TD;
    A[moving_entities]-->B[objects_manager];
    A-->C[drawer_matplotlib];
    B-->D[drawer];
    C-->D;
    D-->E[utils];
```

### 各モジュールの機能

各モジュールは以下の通り。

- **moving_entities**
  - 全体を統合する
- **objects_manager**
  - entityやnutritionなどを管轄する
- **drawer**
  - 描画を行う
  - **drawer_matplotlib**
    - matplotlibを用いて描画を行う
- **utils**
  - 雑多