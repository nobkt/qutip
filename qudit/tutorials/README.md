# Qudit Tutorials

このディレクトリには、Quditシステム（3準位以上の量子系）のシミュレーションに関するチュートリアルが含まれています。

## チュートリアル一覧

### `zeeman_effect_comprehensive.ipynb`

**タイトル**: スピンS=1のゼーマン効果：包括的量子ダイナミクスシミュレーション

**概要**:
スピンS=1系におけるゼーマン効果の量子ダイナミクスを、8つの異なるシミュレーション方法で実装し、それぞれの精度と特性を包括的に比較します。

**シミュレーション方法**:
1. **厳密解 (Exact Solution)**: QuTiPによる行列指数関数計算
2. **鈴木トロッター分解**: 解析的なトロッター分解による時間発展
3. **Qiskit Qubit Statevector**: 2量子ビット符号化とstatevectorシミュレーション
4. **Qiskit Qubit Shot (ノイズ無)**: ショットベースシミュレーション
5. **Qiskit Qubit Shot (ノイズ有)**: ノイズモデルを含むショットシミュレーション
6. **MQT Qudit Statevector**: MQT Quditsによる直接的なqutritシミュレーション
7. **MQT Qudit Shot (ノイズ無)**: MQTショットシミュレーション
8. **MQT Qudit Shot (ノイズ有)**: ノイズを含むMQTショットシミュレーション

**主要な特徴**:
- すべての方法で厳密解との比較と精度評価を実施
- 量子回路のサイズ（ゲート数、深さ）を定量的に報告
- すべての量子回路を可視化
- ヒューリスティックな処理やfallbackは一切使用せず、厳密な理論に基づく実装

**内容**:
1. **システムの定義**: スピンS=1演算子とゼーマン効果のハミルトニアン
2. **8つのシミュレーション方法**: 各方法の詳細な実装とコード
3. **結果の比較**: 期待値とポピュレーションダイナミクスの可視化
4. **精度の定量的評価**: 最大誤差とRMS誤差の計算
5. **量子回路サイズの比較**: ゲート数と回路深さの評価
6. **まとめ**: 各方法の特性と適用範囲

**使用技術**:
- QuTiP (厳密解とトロッター分解)
- Qiskit + Qiskit-Aer (Qubitシミュレーション)
- MQT Qudits (Quditシミュレーション)
- 2量子ビット符号化（Qubit方式）
- ノイズモデル（デポラライジング、振幅減衰）

**学習目標**:
- ゼーマン効果の量子ダイナミクスの理解
- 異なるシミュレーション方法の比較と評価
- Qubit vs Quditアプローチの違い
- ノイズの影響とショット数による統計誤差
- 量子回路の設計と最適化

**前提知識**:
- 量子力学の基礎
- スピン角運動量の理論
- 量子回路の基礎
- Pythonプログラミング

**実行方法**:
```bash
cd qudit/tutorials
jupyter notebook zeeman_effect_comprehensive.ipynb
```

**必要なパッケージ**:
```
# 必須
numpy>=1.22
scipy>=1.8
matplotlib>=3.5
qutip>=5.0
jupyter

# オプション（推奨）
qiskit>=1.0
qiskit-aer>=0.13
mqt.qudits>=1.0
```

**注意事項**:
- Qiskitがインストールされていない場合、Qiskit関連のセクションはスキップされます
- MQT Quditsがインストールされていない場合、MQT関連のセクションはスキップされます
- すべてのパッケージをインストールすることを推奨します

---

### `spin1_qubit_simulation.ipynb`

**タイトル**: スピンS=1量子ダイナミクスの鈴木トロッター分解によるQubitシミュレーション

**概要**:
スピンS=1（3準位系）の量子ダイナミクスを、2量子ビットに符号化し、鈴木トロッター分解を用いて時間発展を計算するアルゴリズムの完全な実装とデモンストレーション。

**内容**:
1. **理論的背景**
   - スピンS=1の数学的構造
   - Qubit符号化の原理
   - 鈴木トロッター分解の理論

2. **実装の検証**
   - Qubit符号化の正確性確認
   - 交換関係の保存検証
   - 状態のencode/decode可逆性

3. **物理例のシミュレーション**
   - **例1: ゼーマン効果** - z軸磁場中のスピン歳差運動
   - **例2: 横磁場中の歳差運動** - 非可換項を含むハミルトニアン
   - **例3: ラビ振動** - 共鳴駆動によるポピュレーション転移

4. **精度の解析**
   - トロッター分解の次数依存性
   - 時間ステップサイズの影響
   - 厳密解との定量的比較

5. **ポピュレーションダイナミクス**
   - 各準位（m=+1, 0, -1）の占有確率の時間発展
   - 厳密解との比較グラフ
   - 誤差の定量評価

**使用技術**:
- 2量子ビット符号化
- 鈴木トロッター分解（1次、2次、4次）
- Statevectorシミュレーション
- QuTiPによる厳密解計算

**学習目標**:
- スピンS=1系の量子ダイナミクスの理解
- Qubit符号化の概念と実装方法
- トロッター分解による時間発展の近似
- 量子アルゴリズムの精度評価方法

**前提知識**:
- 量子力学の基礎（ヒルベルト空間、演算子、時間発展）
- スピン角運動量の理論
- Pythonプログラミングの基礎
- NumPyとMatplotlibの使用経験

**実行方法**:

```bash
# Jupyter Notebookの起動
cd qudit/tutorials
jupyter notebook spin1_qubit_simulation.ipynb
```

または

```bash
# JupyterLabの使用
cd qudit/tutorials
jupyter lab
```

**必要なパッケージ**:
```
numpy>=1.22
scipy>=1.8
matplotlib>=3.5
qutip>=5.0
jupyter
```

インストール:
```bash
pip install numpy scipy matplotlib qutip jupyter
```

**出力**:
ノートブックを実行すると、以下のファイルが生成されます：
- `zeeman_effect_comparison.png` - ゼーマン効果の比較グラフ
- `transverse_field_comparison.png` - 横磁場の比較グラフ
- `rabi_oscillation_comparison.png` - ラビ振動の比較グラフ
- `trotter_accuracy.png` - トロッター分解の精度グラフ

**注意事項**:
- このチュートリアルは厳密な実装に基づいており、ヒューリスティックな近似やfallbackは使用していません
- すべての計算結果は理論的に正当化可能です
- 実行には数分程度かかる場合があります

**関連ドキュメント**:
- `../doc/spin1_quantum_dynamics.md` - スピンS=1の詳細理論
- `../qubit/README.md` - Qubitアルゴリズムの実装詳細

---

### `spin1_qudit_dynamics.ipynb`

**タイトル**: Spin S=1 Quantum Dynamics with Suzuki-Trotter Decomposition

**概要**:
スピンS=1系の量子ダイナミクスをQudit（3準位）として直接扱い、鈴木トロッター分解とMQT Quditsライブラリを用いたシミュレーションを実装します。

**内容**:
1. **数学的基礎**: スピンS=1の角運動量演算子と時間発展
2. **例題1: ゼーマン効果**: 磁場中のスピン歳差運動
3. **例題2: ラビ振動**: 共鳴駆動による準位間遷移
4. **例題3: 2次ゼーマン効果**: 非線形項を含むハミルトニアン
5. **量子回路表現**: QuditゲートとMQT回路の可視化
6. **誤差解析**: 時間ステップ依存性の評価
7. **MQT統合**: MQT Quditsによるstatevectorとショットシミュレーション
8. **ノイズモデル**: デポラライジングと振幅減衰ノイズの実装

**使用技術**:
- QuTiP (基礎理論と厳密解)
- 鈴木トロッター分解（2次、4次）
- MQT Qudits (Quditシミュレーション)
- Qudit量子回路（d=3）
- ノイズモデル

**学習目標**:
- Quditアプローチの理解
- Qubit符号化との比較
- MQT Quditsライブラリの使用方法
- 高次トロッター分解の効果
- ノイズの影響とエラー軽減

**実行方法**:
```bash
cd qudit/tutorials
jupyter notebook spin1_qudit_dynamics.ipynb
```

**必要なパッケージ**:
```
numpy>=1.22
scipy>=1.8
matplotlib>=3.5
qutip>=5.0
jupyter
mqt.qudits>=1.0  # オプション
```

## トラブルシューティング

### QuTiPのインポートエラー
```python
ModuleNotFoundError: No module named 'qutip'
```

**解決方法**:
```bash
pip install qutip
```

### Jupyter Notebookが起動しない
```bash
pip install --upgrade jupyter notebook
```

### グラフが表示されない
ノートブックの最初のセルに以下を追加:
```python
%matplotlib inline
```

### メモリ不足エラー
時間ステップ数を減らすか、シミュレーション時間を短くしてください：
```python
times = np.linspace(0, 2.0, 50)  # 100 → 50に減らす
```

## 今後の拡張

以下のトピックについてのチュートリアル追加を計画しています：

1. **開放系のダイナミクス**: リンドブラッドマスター方程式のQubitシミュレーション
2. **高次スピン系**: S > 1 のシステムへの拡張
3. **多体系**: 複数のスピンS=1粒子の相互作用
4. **量子もつれ**: スピンS=1系でのエンタングルメント解析
5. **量子制御**: 最適制御理論の応用

## フィードバック

チュートリアルへのフィードバックや改善提案は歓迎します。
GitHubのIssueやPull Requestをご利用ください。

## ライセンス

これらのチュートリアルはQuTiPプロジェクトの一部として配布されます。

## Triplet-Triplet Annihilation (TTA) Simulation

### Files

- **[triplet_triplet_annihilation_theory.md](triplet_triplet_annihilation_theory.md)**: Complete theoretical documentation with detailed mathematical formulas
- **[triplet_triplet_annihilation.ipynb](triplet_triplet_annihilation.ipynb)**: Comprehensive Jupyter notebook implementation
- **[TTA_IMPLEMENTATION_SUMMARY.md](TTA_IMPLEMENTATION_SUMMARY.md)**: Implementation summary and completion report

### Overview

This tutorial simulates the quantum dynamics of triplet-triplet annihilation (TTA) in two dye molecules A and B. The system includes:

- **Electronic states**: Ground singlet (S₀), excited triplet (T₁), excited singlet (S₁)
- **Processes**: Energy transfer (T₁ ↔ S₀) and triplet-triplet annihilation (T₁ + T₁ → S₁ + S₀)
- **Initial state**: Molecule A in T₁, Molecule B in S₀

### Implementations

1. **Classical rate equation model**: ODE-based kinetic simulation
2. **Quantum mechanical description**: Exact Hamiltonian evolution
3. **Qubit representation (Qiskit)**: 4-qubit encoding with quantum circuits
4. **Qudit representation (MQT)**: 2-qutrit encoding with quantum circuits

All implementations use Suzuki-Trotter decomposition for time evolution and include both statevector and shot-based simulations.

### Features

- Complete mathematical theory with no omissions
- Comparative analysis of classical vs quantum models
- Qubit vs Qudit resource comparison
- Circuit analysis (qubit/qudit count, gate count, depth)
- Circuit visualization
- Population dynamics visualization

### Requirements

- Python 3.9+
- NumPy, SciPy, Matplotlib
- QuTiP
- Qiskit (optional, for qubit simulations)
- MQT modules (optional, for qudit simulations)

### Usage

```bash
jupyter notebook triplet_triplet_annihilation.ipynb
```

For detailed theory, refer to `triplet_triplet_annihilation_theory.md`.

