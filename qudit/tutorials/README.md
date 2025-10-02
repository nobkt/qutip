# Qudit Tutorials

このディレクトリには、Quditシステム（3準位以上の量子系）のシミュレーションに関するチュートリアルが含まれています。

## チュートリアル一覧

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
