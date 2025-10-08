# Qudit Documentation

このディレクトリには、QuTiPにおける3準位以上の量子系（qudit）に関する詳細な理論文書が含まれています。

## ファイル一覧

### installation.md
quditモジュールのインストール手順書（日本語）

#### 内容
- quditモジュールの概要と主な機能
- 必要要件（必須パッケージとオプションパッケージ）
- インストール方法
  - 開発モードでのインストール（推奨）
  - ソースからの直接インストール
  - Jupyter Notebookでの使用
- インストールの検証手順
- クイックスタートガイド
- トラブルシューティング
- アンインストール方法

#### 対象読者
- quditモジュールを初めて使用する方
- QuTiPの拡張機能を利用したい研究者・学生
- スピンS=1のシミュレーションを行いたい方

#### 特徴
- ステップバイステップのインストール手順
- 複数のインストール方法を提供
- よくある問題と解決方法を掲載
- 実践的なクイックスタートガイド

### spin1_quantum_dynamics.md
スピンS=1の量子ダイナミクスの完全な理論解説文書（日本語）

#### 内容
- ヒルベルト空間の構造と基底状態
- スピン演算子の定義と性質
- 交換関係と固有値問題
- 行列表現と計算例
- 時間発展とシュレディンガー方程式
- 各種ハミルトニアン（ゼーマン効果、二次ゼーマン効果、スピン-スピン相互作用など）
- スピンコヒーレント状態
- 密度行列形式と混合状態
- 開放系のリンドブラッドマスター方程式
- QuTiPでの実装例とコードサンプル
- 数学的補足と参考文献

#### 対象読者
- 量子力学とスピン系の基礎知識を持つ研究者・学生
- QuTiPを用いてスピン1系のシミュレーションを行いたい方
- 量子情報におけるqutrit（3準位量子ビット）を学びたい方

#### 特徴
- 数式を省略せず、完全な導出を記載
- 理論から実装まで一貫した説明
- QuTiPのコード例を豊富に掲載
- 1200行以上の包括的な内容

### 量子回路可視化のドキュメント (NEW - 2024年10月)

#### CIRCUIT_VISUALIZATION_DOCUMENTATION.md (英語)
完全なqudit（3準位）量子回路可視化機能のドキュメント

**内容:**
- 詳細な数学的理論（ヒルベルト空間、角運動量演算子、鈴木-Trotter分解）
- QuditCircuitとQuditGateクラスの完全な仕様
- 回路可視化機能（色分け、数式表示、複数行対応）
- 状態発展可視化（占有確率、期待値、Bloch球面軌跡）
- 使用例とコードサンプル
- テスト結果とパフォーマンス情報

**対象読者:**
- ネイティブqudit実装を理解したい研究者
- 量子回路の可視化機能を使用したい開発者
- Spin S=1システムのシミュレーションを行う方

#### CIRCUIT_VISUALIZATION_JAPANESE.md (日本語)
上記ドキュメントの日本語版

**特徴:**
- すべての実装が厳密（ヒューリスティックなしfallbackなし）
- ユニタリ性の検証付き
- 包括的なテストスイート（12項目すべて成功）
- 出版品質の可視化

**images/**: 量子回路可視化の例
- `example_circuit_orders.png`: 異なるトロッター次数の比較
- `example_circuit_mixed.png`: 混合ハミルトニアン (Jz + Jx)
- `circuit_simple.png`: 基本的な回路図

## 量子回路可視化 (2024年10月更新)

スピンS=1量子ダイナミクスの**ネイティブqudit（3準位）量子回路可視化機能**が実装されました。

### 主な機能
- **ネイティブ3準位系**: 2qubitエンコーディングなし、直接的なqutrit表現
- **完全な数学的理論**: ヒルベルト空間から鈴木-Trotter分解まで
- **回路の自動生成**: SimulatorからQuditCircuitオブジェクトを取得
- **高品質な可視化**:
  - 色分けされたゲート（Jx:赤、Jy:ティール、Jz:薄ティール）
  - 数式表示（LaTeX形式）
  - 複数行対応（長い回路も見やすく）
- **状態発展可視化**:
  - 占有確率のプロット
  - 期待値の時間発展
  - Bloch球面上の軌跡（3Dと2D投影）
- **厳密な実装**: ヒューリスティックなし、fallbackなし

### 使用例

```python
from qudit.qudit import (
    StatevectorSimulator,
    get_spin1_operators,
    visualize_state_evolution,
    visualize_bloch_sphere_trajectory
)
import numpy as np

# セットアップ
ops = get_spin1_operators()
Jz = ops['Jz']
H = -2 * np.pi * Jz  # ゼーマン・ハミルトニアン

# 回路生成付きシミュレーション
times = np.linspace(0, 1.0, 11)
states = get_spin1_states()
psi0 = states['m1']

sim = StatevectorSimulator(trotter_order=2, decomposition_basis='xyz')
result = sim.simulate(H, psi0, times, return_circuit=True)

# 回路の可視化
circuit = result['circuit']
fig, axes = circuit.visualize(figsize=(16, 6), show_math=True)
plt.savefig('my_circuit.png', dpi=150)
plt.show()

# 状態発展の可視化
fig, axes = visualize_state_evolution(
    result['states'], times,
    operators={'Jx': ops['Jx'], 'Jy': ops['Jy'], 'Jz': ops['Jz']}
)
plt.savefig('state_evolution.png', dpi=150)

# Bloch球面軌跡
fig, ax = visualize_bloch_sphere_trajectory(
    result['states'], projection='3d'
)
plt.savefig('bloch_trajectory.png', dpi=150)
```

### 強化されたチュートリアル

`tutorials/spin1_qudit_dynamics.ipynb` が大幅に強化されました：
- セル数: 23 → 40（17セル追加）
- 数学的理論の詳細説明（6セル）
- 量子回路の生成と可視化（7セル）
- 高度な状態可視化（4セル）

詳細なドキュメントは以下を参照：
- 英語: `CIRCUIT_VISUALIZATION_DOCUMENTATION.md`
- 日本語: `CIRCUIT_VISUALIZATION_JAPANESE.md`

## 関連リソース

- [QuTiP公式ドキュメント](https://qutip.org/docs/latest/)
- [QuTiPチュートリアル](https://github.com/qutip/qutip-tutorials)
- [QuTiP論文](https://www.sciencedirect.com/science/article/pii/S0010465512003955)

## ライセンス

これらの文書はQuTiPプロジェクトの一部として配布されます。
