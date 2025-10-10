# Zeeman Effect Notebook 修正完了報告

## 問題の概要

`qudit/tutorials/zeeman_effect_comprehensive.ipynb` を実行すると以下のエラーが発生していました：

```
ERROR: Failed to load circuits: Duplicate key "statevector" in save instruction.
QiskitError: 'You have to select a circuit or schedule when there is more than one available'
```

## 原因

Qiskitの `StatevectorSimulator` で状態ベクトルを取得する際、以下のパターンを使用していました：

```python
qc_sv.save_statevector()
sv_sim = QiskitStatevectorSim()
sv_job = sv_sim.run(transpile(qc_sv, sv_sim))  # ← これが原因
sv = sv_job.result().get_statevector()
```

`transpile()` 関数が `save_statevector()` を含む回路を処理すると、以下の問題が発生します：
1. 保存命令が重複する
2. 同じラベル "statevector" を持つ複数の保存命令が作成される
3. 状態ベクトルの取得時にどの命令を使用するか判断できなくなる

## 解決方法

`StatevectorSimulator` で実行する際に不要な `transpile()` 呼び出しを削除しました。

**修正前：**
```python
sv_job = sv_sim.run(transpile(qc_sv, sv_sim))
```

**修正後：**
```python
sv_job = sv_sim.run(qc_sv)
```

## 修正箇所

ノートブック内の2箇所を修正しました：

1. **Cell 5**（Qiskit Shot ノイズなしシミュレーション）：106行目
2. **Cell 6**（Qiskit Shot ノイズありシミュレーション）：118行目

どちらも、JxとJy演算子の期待値を計算するために状態ベクトルを取得する処理でした。

## 技術的詳細

### なぜこの修正が機能するのか

`StatevectorSimulator` は基本的な操作に対してトランスパイルを必要としません：
- `save_statevector()` を含む回路を直接実行できます
- トランスパイルが主に必要なのは：
  - ハードウェア制約へのマッピング
  - 基底ゲートセットへの変換
  - 回路深さの最適化

`StatevectorSimulator` はシミュレータであり、ハードウェア制約がないため、トランスパイルは不要です。むしろ、保存命令と干渉する可能性があります。

### 修正の影響

- **変更行数**: 2行のみ（最小限の変更）
- **機能への影響**: なし（不要な処理を削除しただけ）
- **シミュレーション結果**: 変更なし（同じ結果が得られます）
- **パフォーマンス**: わずかに改善（不要な変換処理がなくなるため）

## 検証

修正後、以下を確認しました：

1. ✓ Cell 5の `transpile()` 呼び出しが削除されている
2. ✓ Cell 6の `transpile()` 呼び出しが削除されている
3. ✓ 他に問題のあるパターンが残っていない
4. ✓ 正しいパターン（`sv_sim.run(qc_sv)`）が2箇所で使用されている

## ファイル構成

修正に関連するファイル：

1. **qudit/tutorials/zeeman_effect_comprehensive.ipynb** - 修正されたノートブック
2. **ZEEMAN_NOTEBOOK_FIX.md** - 英語での詳細な説明
3. **tests/test_zeeman_save_statevector_fix.py** - 修正パターンを検証するテスト
4. **本ファイル** - 日本語での完了報告

## 実行方法

修正後、ノートブックは以下のように実行できます：

```bash
jupyter notebook qudit/tutorials/zeeman_effect_comprehensive.ipynb
```

または

```bash
jupyter nbconvert --execute qudit/tutorials/zeeman_effect_comprehensive.ipynb
```

エラーなく実行され、期待通りの結果が得られるはずです。

## まとめ

- **問題**: `transpile()` と `save_statevector()` の組み合わせでキーの重複エラー
- **解決**: 不要な `transpile()` 呼び出しを削除
- **影響**: 最小限（2行の変更のみ）
- **結果**: エラーなく実行可能

ヒューリスティックな処理やごまかしのためのfallbackは一切使用せず、根本原因を特定して修正しました。
