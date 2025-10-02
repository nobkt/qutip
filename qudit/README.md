# Qudit - 高次元量子系シミュレーションモジュール

`qudit` は、QuTiP (Quantum Toolbox in Python) の拡張モジュールで、3準位以上の量子系（qudit）のシミュレーションを提供します。

## 概要

このモジュールは、スピンS=1（qutrit）系を2量子ビット空間に符号化し、鈴木トロッター分解を用いて効率的に時間発展をシミュレートする機能を実装しています。

### 主な機能

- **スピンS=1の量子ビット符号化**: 3次元ヒルベルト空間を4次元量子ビット空間に埋め込み
- **鈴木トロッター分解**: 1次、2次、4次の高精度時間発展アルゴリズム
- **状態ベクトルシミュレータ**: 効率的な量子ダイナミクスシミュレーション
- **量子回路可視化**: トロッター分解された回路の可視化機能
- **厳密解との比較**: QuTiPの厳密ソルバーとの精度検証機能

## クイックスタート

### インストール

**詳細なインストール手順は [doc/installation.md](doc/installation.md) を参照してください。**

基本的なインストール手順：

```bash
# QuTiPリポジトリをクローン
git clone https://github.com/qutip/qutip.git
cd qutip

# QuTiPをインストール
pip install -e .

# quditモジュールを使用可能にする
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 簡単な使用例

```python
import numpy as np
import qutip as qt
from qudit.qubit import StatevectorSimulator

# ゼーマンハミルトニアンの定義
omega0 = 2 * np.pi * 1.0  # 周波数（GHz）
Jz = qt.jmat(1, 'z')
H = -omega0 * Jz

# 初期状態
psi0 = qt.spin_coherent(1, np.pi/2, 0)

# 時間配列
times = np.linspace(0, 2.0, 100)

# シミュレーション実行
simulator = StatevectorSimulator(trotter_order=2)
result = simulator.simulate(H, psi0, times)

# 結果の取得
populations = result['populations']
expectations = result['expect']
```

## ディレクトリ構造

```
qudit/
├── doc/                    # ドキュメント
│   ├── README.md          # ドキュメント索引
│   ├── installation.md    # インストールガイド（日本語）
│   ├── spin1_quantum_dynamics.md  # スピンS=1の理論
│   └── images/            # 図表
├── qubit/                 # 量子ビットアルゴリズム実装
│   ├── __init__.py
│   ├── spin1_encoding.py  # スピン-1符号化
│   ├── trotter_decomposition.py  # トロッター分解
│   ├── statevector_simulator.py  # シミュレータ
│   ├── circuit_visualization.py  # 回路可視化
│   ├── README.md          # アルゴリズム詳細
│   └── CIRCUIT_VISUALIZATION.md  # 可視化機能の説明
└── tutorials/             # チュートリアルノートブック
    ├── README.md
    └── spin1_qubit_simulation.ipynb
```

## ドキュメント

### 入門

- **[doc/installation.md](doc/installation.md)** - インストールガイド（推奨！）
  - 必要要件
  - ステップバイステップのインストール手順
  - 動作確認方法
  - トラブルシューティング

### 理論

- **[doc/spin1_quantum_dynamics.md](doc/spin1_quantum_dynamics.md)** - スピンS=1の量子ダイナミクス
  - ヒルベルト空間の構造
  - スピン演算子の定義と性質
  - 時間発展とシュレディンガー方程式
  - 各種ハミルトニアン
  - QuTiP実装例

### 実装

- **[qubit/README.md](qubit/README.md)** - 量子ビットアルゴリズムの詳細
  - スピン-1符号化スキーム
  - 鈴木トロッター分解の理論
  - 状態ベクトルシミュレータの使用法
  - 精度評価

- **[qubit/CIRCUIT_VISUALIZATION.md](qubit/CIRCUIT_VISUALIZATION.md)** - 量子回路可視化機能
  - テキスト形式とグラフィカル形式の出力
  - 回路の深さとゲート数の分析

### チュートリアル

- **[tutorials/spin1_qubit_simulation.ipynb](tutorials/spin1_qubit_simulation.ipynb)** - 実践的なチュートリアル
  - 基本的なシミュレーション例
  - 各種ハミルトニアンの実装
  - トロッター分解の精度比較
  - 回路可視化の実例

## 必要要件

- Python 3.9+
- QuTiP 5.0+
- NumPy 1.22+
- SciPy 1.8+
- Matplotlib 3.5+（回路可視化用、オプション）

詳細は [doc/installation.md](doc/installation.md) を参照してください。

## 使用例

### 例1: 基本的なシミュレーション

```python
from qudit.qubit import StatevectorSimulator
import qutip as qt
import numpy as np

# シミュレータの初期化
simulator = StatevectorSimulator(trotter_order=2)

# ハミルトニアンの定義
Jz = qt.jmat(1, 'z')
H = 2 * np.pi * Jz

# 時間発展
psi0 = qt.basis(3, 0)
times = np.linspace(0, 1.0, 50)
result = simulator.simulate(H, psi0, times)
```

### 例2: 厳密解との比較

```python
comparison = simulator.compare_with_exact(H, psi0, times)
print(f"最大誤差: {comparison['errors']['max_expect_error']:.2e}")
```

### 例3: 量子回路の可視化

```python
fig, ax, circuit = simulator.visualize_circuit(
    H, times[:10],
    title="量子回路: ゼーマン効果"
)
plt.show()
```

## テストとベンチマーク

実装の正確性は以下によって保証されています：

1. **交換関係の検証**: 符号化された演算子が正しい交換関係 `[Ji, Jj] = i*εijk*Jk` を満たすことを確認
2. **状態の可逆性**: encode/decode が可逆写像であることを確認（Fidelity > 1 - 10⁻¹⁰）
3. **厳密解との比較**: QuTiPの厳密ソルバーとの一致を確認（典型的誤差 < 10⁻⁶）
4. **ポピュレーション保存**: 確率の総和が1であることを各時刻で確認

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. **ModuleNotFoundError**: Pythonパスに qudit ディレクトリが含まれているか確認
2. **ImportError**: QuTiPが正しくインストールされているか確認
3. **数値精度の問題**: トロッター分解の次数を上げるか、時間ステップを細かくする

詳細なトラブルシューティングは [doc/installation.md](doc/installation.md) を参照してください。

## 理論的背景

### スピンS=1の数学的構造

スピンS=1系は3次元ヒルベルト空間を持ち、基底状態は：

```
|1, +1⟩ = [1, 0, 0]ᵀ
|1,  0⟩ = [0, 1, 0]ᵀ
|1, -1⟩ = [0, 0, 1]ᵀ
```

スピン演算子（ℏ = 1）の行列表現：

```
Jz = diag(1, 0, -1)

Jx = (1/√2) [0  1  0]
            [1  0  1]
            [0  1  0]

Jy = (1/√2) [0  -i  0]
            [i   0 -i]
            [0   i  0]
```

これらは交換関係 `[Jx, Jy] = iJz` などを満たします。

### 量子ビット符号化

3次元のスピン-1を4次元の2量子ビット空間に埋め込みます：

```
|m=+1⟩ → |00⟩
|m= 0⟩ → |01⟩
|m=-1⟩ → |10⟩
|11⟩   → 未使用
```

この符号化により、スピン演算子の交換関係と固有値が保存されます。

### 鈴木トロッター分解

ハミルトニアン H = H₁ + H₂ + ... + Hₙ の時間発展演算子を近似：

- **1次** (Lie-Trotter): 誤差 O(Δt²)
- **2次** (Strang splitting): 誤差 O(Δt³)
- **4次** (Yoshida): 誤差 O(Δt⁵)

## 参考文献

### 理論

1. J.J. Sakurai, "Modern Quantum Mechanics" - 角運動量理論
2. Nielsen & Chuang, "Quantum Computation and Quantum Information"
3. H.F. Trotter, "On the product of semi-groups of operators" (1959)
4. M. Suzuki, "Fractal decomposition of exponential operators" (1990)

### 実装

5. QuTiP Documentation - https://qutip.org/
6. QuTiP論文: [Computer Physics Communications 184, 1234 (2013)](https://www.sciencedirect.com/science/article/pii/S0010465512003955)

## コントリビューション

バグ報告や機能リクエストは、GitHubのIssuesで受け付けています：
https://github.com/qutip/qutip/issues

## ライセンス

このモジュールは、QuTiPプロジェクトの一部として、BSD 3-Clause Licenseの下で配布されています。

---

**For English documentation**, please refer to the main QuTiP documentation at https://qutip.org/

**始めるには**: [doc/installation.md](doc/installation.md) のインストールガイドを参照してください。
