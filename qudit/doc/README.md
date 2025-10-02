# Qudit Documentation

このディレクトリには、QuTiPにおける3準位以上の量子系（qudit）に関する詳細な理論文書が含まれています。

## ファイル一覧

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

### 量子回路可視化のドキュメント (NEW)

**images/**: 量子回路可視化の例
- `example_circuit_orders.png`: 異なるトロッター次数の比較
- `example_circuit_mixed.png`: 混合ハミルトニアン (Jz + Jx)
- `circuit_simple.png`: 基本的な回路図

詳細は `../qubit/CIRCUIT_VISUALIZATION.md` を参照してください。

## 量子回路可視化

鈴木トロッター分解によるスピンS=1量子ダイナミクスの量子回路可視化機能が実装されました。

### 主な機能
- テキスト形式とグラフィカル形式の回路図出力
- 1次、2次、4次トロッター分解の可視化
- ハミルトニアンの自動分解
- チュートリアルノートブックとの統合

### 使用例

```python
from qudit.qubit import StatevectorSimulator
import qutip as qt
import numpy as np

simulator = StatevectorSimulator(trotter_order=2)
H = 2 * np.pi * qt.jmat(1, 'z')
times = np.linspace(0, 1.0, 20)

# 回路の取得
circuit = simulator.get_circuit(H, times)
print(f"ゲート数: {len(circuit.gates)}")
print(f"回路の深さ: {circuit.depth()}")

# 回路の可視化
fig, ax, circuit = simulator.visualize_circuit(
    H, times, 
    title="量子回路: ゼーマン効果"
)
plt.show()
```

詳細なドキュメントは `../qubit/CIRCUIT_VISUALIZATION.md` を参照してください。

## 関連リソース

- [QuTiP公式ドキュメント](https://qutip.org/docs/latest/)
- [QuTiPチュートリアル](https://github.com/qutip/qutip-tutorials)
- [QuTiP論文](https://www.sciencedirect.com/science/article/pii/S0010465512003955)

## ライセンス

これらの文書はQuTiPプロジェクトの一部として配布されます。
