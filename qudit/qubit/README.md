# Qubit Algorithm Implementation for Spin S=1

このディレクトリには、スピンS=1（3準位系）の量子ダイナミクスを2量子ビットに符号化し、鈴木トロッター分解を用いてシミュレートするアルゴリズムの実装が含まれています。

## ファイル構成

### コアモジュール

#### `spin1_encoding.py`
スピンS=1の3準位系を2量子ビット（4次元）空間に符号化するモジュール。

**主要機能:**
- `Spin1QubitEncoding`: 符号化クラス
  - `encode_state()`: スピン-1状態を2量子ビット状態に変換
  - `decode_state()`: 2量子ビット状態からスピン-1状態へ逆変換
  - `encode_Jx()`, `encode_Jy()`, `encode_Jz()`: スピン演算子の符号化
  - `encode_Jp()`, `encode_Jm()`: 昇降演算子の符号化
  - `verify_commutation_relations()`: 交換関係の検証

**符号化スキーム:**
```
|m=+1⟩ → |00⟩
|m= 0⟩ → |01⟩
|m=-1⟩ → |10⟩
|11⟩   → 未使用
```

**理論的保証:**
- スピン演算子の交換関係 `[Ji, Jj] = i*εijk*Jk` を厳密に保存
- 固有値と固有状態の対応を保持
- ユニタリ性を保証

#### `trotter_decomposition.py`
鈴木トロッター分解による時間発展演算子の近似。

**主要機能:**
- `SuzukiTrotterDecomposition`: トロッター分解クラス
  - `first_order_step()`: 1次Lie-Trotter分解（誤差 O(Δt²)）
  - `second_order_step()`: 2次Strang splitting（誤差 O(Δt³)）
  - `fourth_order_step()`: 4次Yoshida分解（誤差 O(Δt⁵)）
  - `evolve_state()`: 状態の時間発展
  - `compute_expectation_values()`: 期待値の計算

**理論:**

1次分解（Lie-Trotter）:
```
exp(-i(H₁ + H₂)Δt) ≈ exp(-iH₁Δt)exp(-iH₂Δt) + O(Δt²)
```

2次分解（Strang splitting）:
```
exp(-i(H₁ + H₂)Δt) ≈ exp(-iH₁Δt/2)exp(-iH₂Δt)exp(-iH₁Δt/2) + O(Δt³)
```

4次分解（Yoshida）:
```
S₄(Δt) = S₂(pΔt)S₂(pΔt)S₂((1-4p)Δt)S₂(pΔt)S₂(pΔt)
ここで p = 1/(4 - 4^(1/3))
```

#### `statevector_simulator.py`
状態ベクトルシミュレータ。符号化とトロッター分解を組み合わせて、スピン-1のダイナミクスを計算。

**主要機能:**
- `StatevectorSimulator`: シミュレータクラス
  - `simulate()`: スピン-1ハミルトニアンの時間発展をシミュレート
  - `compare_with_exact()`: QuTiPの厳密解と比較

**出力:**
- 各時刻での状態ベクトル
- スピン演算子の期待値の時間発展
- ポピュレーションダイナミクス（各準位の占有確率）
- 厳密解との誤差評価

## 使用方法

### 基本的な使い方

```python
import numpy as np
import qutip as qt
from qudit.qubit import StatevectorSimulator

# ハミルトニアンの定義（スピンS=1）
omega0 = 2 * np.pi * 1.0
Jz = qt.jmat(1, 'z')
H = -omega0 * Jz

# 初期状態
psi0 = qt.spin_coherent(1, np.pi/2, 0)

# 時間配列
times = np.linspace(0, 2.0, 100)

# シミュレータの初期化（2次トロッター分解）
simulator = StatevectorSimulator(trotter_order=2)

# シミュレーション実行
result = simulator.simulate(H, psi0, times)

# 期待値の取得
Jx_expect = result['expect'][:, 0]
Jy_expect = result['expect'][:, 1]
Jz_expect = result['expect'][:, 2]

# ポピュレーションの取得
pop_m1 = result['populations'][:, 0]  # P(m=+1)
pop_0 = result['populations'][:, 1]   # P(m=0)
pop_m_1 = result['populations'][:, 2] # P(m=-1)
```

### 厳密解との比較

```python
# 厳密解との比較
comparison = simulator.compare_with_exact(
    hamiltonian=H,
    initial_state=psi0,
    times=times
)

# 誤差の確認
print(f"最大期待値誤差: {comparison['errors']['max_expect_error']:.2e}")
print(f"平均期待値誤差: {comparison['errors']['mean_expect_error']:.2e}")
print(f"最大ポピュレーション誤差: {comparison['errors']['max_pop_error']:.2e}")
```

### トロッター分解の次数の選択

```python
# 1次トロッター（高速だが精度は低い）
simulator1 = StatevectorSimulator(trotter_order=1)

# 2次トロッター（バランスが良い、推奨）
simulator2 = StatevectorSimulator(trotter_order=2)

# 4次トロッター（高精度だが計算コストが高い）
simulator4 = StatevectorSimulator(trotter_order=4)
```

## 理論的背景

### スピンS=1の数学的構造

スピンS=1系は3次元ヒルベルト空間 ℋ₃ を持ちます。基底状態は：

```
|1, +1⟩ = [1, 0, 0]ᵀ
|1,  0⟩ = [0, 1, 0]ᵀ
|1, -1⟩ = [0, 0, 1]ᵀ
```

スピン演算子（ℏ = 1）:

```
Jz = diag(1, 0, -1)

Jx = (1/√2) [0  1  0]
            [1  0  1]
            [0  1  0]

Jy = (1/√2) [0  -i  0]
            [i   0 -i]
            [0   i  0]
```

交換関係:
```
[Jx, Jy] = iJz
[Jy, Jz] = iJx
[Jz, Jx] = iJy
```

### Qubit符号化の正当性

2量子ビット空間（4次元）に3次元のスピン-1を埋め込みます。符号化された演算子は元の交換関係を保存します。

**証明可能な性質:**
1. 符号化写像はヒルベルト空間の部分空間への埋め込み
2. 埋め込まれた部分空間で演算子の代数構造を保存
3. ユニタリ時間発展は正しく再現される

### 鈴木トロッター分解の収束性

ハミルトニアン H = H₁ + H₂ + ... + Hₙ に対して：

**定理（Trotter-Suzuki）:**
k次のトロッター分解を用いた場合、時間発展演算子の近似誤差は O(Δt^(k+1)) となる。

**実装での保証:**
- 1次: ε ∝ Δt²
- 2次: ε ∝ Δt³
- 4次: ε ∝ Δt⁵

## テストとベンチマーク

実装の正確性は以下によって保証されています：

1. **交換関係の検証**: 符号化された演算子が正しい交換関係を満たすことを数値的に確認
2. **状態の可逆性**: encode/decode が可逆写像であることを確認（Fidelity > 1 - 10⁻¹⁰）
3. **厳密解との比較**: QuTiPの厳密ソルバーとの一致を確認（典型的誤差 < 10⁻⁶）
4. **ポピュレーション保存**: 確率の総和が1であることを各時刻で確認

## 参考文献

### 理論
1. J.J. Sakurai, "Modern Quantum Mechanics" - 角運動量理論
2. Nielsen & Chuang, "Quantum Computation and Quantum Information" - 量子アルゴリズム
3. H.F. Trotter, "On the product of semi-groups of operators" (1959) - トロッター積公式
4. M. Suzuki, "Fractal decomposition of exponential operators" (1990) - 高次分解

### 実装
5. QuTiP Documentation - https://qutip.org/
6. "Quantum algorithms for quantum dynamics" - Reviews of Modern Physics

## ライセンス

このコードはQuTiPプロジェクトの一部として、同じライセンスの下で配布されます。
