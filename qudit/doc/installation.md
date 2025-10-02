# Qudit モジュール インストールガイド

このドキュメントでは、QuTiP の `qudit` モジュールのインストール方法と、その機能を利用可能にする手順を説明します。

## 目次

1. [概要](#概要)
2. [必要要件](#必要要件)
3. [インストール方法](#インストール方法)
4. [インストールの検証](#インストールの検証)
5. [クイックスタート](#クイックスタート)
6. [トラブルシューティング](#トラブルシューティング)
7. [アンインストール](#アンインストール)

## 概要

`qudit` モジュールは、3準位以上の量子系（qudit）のシミュレーションを行うための拡張機能を提供します。特に、スピンS=1（qutrit）系を2量子ビットに符号化し、鈴木トロッター分解を用いて時間発展をシミュレートする機能が実装されています。

### 主な機能

- **スピンS=1の量子ビット符号化**: 3準位系を2量子ビット空間に埋め込み
- **鈴木トロッター分解**: 1次、2次、4次の高精度時間発展
- **状態ベクトルシミュレータ**: 効率的な量子ダイナミクスシミュレーション
- **量子回路可視化**: トロッター分解された回路の可視化機能
- **厳密解との比較**: QuTiPの厳密ソルバーとの精度検証

## 必要要件

### 必須パッケージ

`qudit` モジュールを使用するには、以下のパッケージが必要です：

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| **Python** | 3.9+ | プログラミング言語 |
| **QuTiP** | 5.0+ | 量子ツールボックス（基本機能） |
| **NumPy** | 1.22+ | 数値計算 |
| **SciPy** | 1.8+ | 科学技術計算 |

### オプションパッケージ

以下のパッケージは、特定の機能を使用する場合に必要です：

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| **Matplotlib** | 3.5+ | 回路図の可視化、プロット作成 |
| **Jupyter** | - | チュートリアルノートブックの実行 |
| **pytest** | 5.3+ | テストの実行 |

## インストール方法

`qudit` モジュールは、QuTiPリポジトリに含まれていますが、標準の `pip install qutip` では自動的にインストールされません。以下の方法でインストールしてください。

### 方法1: 開発モードでのインストール（推奨）

この方法は、`qudit` モジュールを変更したり、最新の開発版を使用したい場合に推奨されます。

#### ステップ1: リポジトリのクローン

```bash
# QuTiPリポジトリをクローン
git clone https://github.com/qutip/qutip.git
cd qutip
```

または、フォークしたリポジトリからクローンする場合：

```bash
git clone https://github.com/YOUR_USERNAME/qutip.git
cd qutip
```

#### ステップ2: 仮想環境の作成（推奨）

システムのPython環境を汚さないために、仮想環境を使用することを強く推奨します。

```bash
# 仮想環境の作成
python -m venv qutip-env

# 仮想環境の有効化（Linux/macOS）
source qutip-env/bin/activate

# 仮想環境の有効化（Windows）
qutip-env\Scripts\activate
```

#### ステップ3: QuTiPの開発版インストール

```bash
# 必要な依存関係のインストール
pip install --upgrade pip setuptools wheel

# QuTiPを開発モードでインストール
python setup.py develop
```

または、`pip` を使用する場合：

```bash
pip install -e .
```

開発モードでインストールすると、ソースコードの変更が即座に反映されます。Cythonファイルを変更した場合は、再ビルドが必要です。

#### ステップ4: qudit モジュールのPythonパスへの追加

`qudit` ディレクトリをPythonパスに追加することで、モジュールをインポート可能にします。

**方法A: 環境変数の設定（一時的）**

```bash
# Linux/macOS
export PYTHONPATH="${PYTHONPATH}:/path/to/qutip"

# Windows（コマンドプロンプト）
set PYTHONPATH=%PYTHONPATH%;C:\path\to\qutip

# Windows（PowerShell）
$env:PYTHONPATH += ";C:\path\to\qutip"
```

**方法B: スクリプト内でパスを追加**

Pythonスクリプトやノートブックの最初に以下を追加：

```python
import sys
sys.path.insert(0, '/path/to/qutip')
```

**方法C: .pth ファイルの作成（永続的）**

仮想環境のsite-packagesディレクトリに `.pth` ファイルを作成：

```bash
# 仮想環境のsite-packagesディレクトリを確認
python -c "import site; print(site.getsitepackages())"

# .pth ファイルを作成（パスは適宜変更）
echo "/path/to/qutip" > /path/to/venv/lib/python3.x/site-packages/qutip-qudit.pth
```

### 方法2: ソースからの直接インストール

QuTiPの完全インストール後に、`qudit` モジュールだけを使用する場合の方法です。

```bash
# QuTiPをインストール（まだインストールしていない場合）
pip install qutip

# リポジトリをクローン
git clone https://github.com/qutip/qutip.git
cd qutip

# Pythonパスに追加（上記の方法A、B、Cのいずれかを使用）
```

### 方法3: Jupyter Notebookでの使用

チュートリアルノートブックを直接実行する場合：

```bash
# リポジトリをクローン
git clone https://github.com/qutip/qutip.git
cd qutip

# Jupyter Notebookをインストール（まだの場合）
pip install jupyter

# ノートブックを起動
jupyter notebook qudit/tutorials/spin1_qubit_simulation.ipynb
```

ノートブックの最初のセルで以下を実行：

```python
import sys
import os

# quditモジュールのパスを追加
repo_root = os.path.abspath('../..')
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# インポートの確認
from qudit.qubit import StatevectorSimulator
print("qudit モジュールのインポートに成功しました！")
```

## インストールの検証

インストールが正常に完了したか確認するために、以下のコマンドを実行してください。

### 基本的な検証

```python
# Pythonインタプリタまたはスクリプトで実行
import qutip as qt
import numpy as np

# QuTiPの動作確認
print("QuTiP version:", qt.__version__)
qt.about()

# qudit モジュールのインポート確認
from qudit.qubit import (
    Spin1QubitEncoding,
    StatevectorSimulator,
    SuzukiTrotterDecomposition
)

print("\n✓ qudit モジュールのインポートに成功しました！")
```

期待される出力：
```
QuTiP version: 5.x.x
QuTiP: Quantum Toolbox in Python
================================
...

✓ qudit モジュールのインポートに成功しました！
```

### 動作確認テスト

より詳細な動作確認を行う場合：

```python
import numpy as np
import qutip as qt
from qudit.qubit import StatevectorSimulator

# シミュレータの初期化
simulator = StatevectorSimulator(trotter_order=2)
print("✓ シミュレータの初期化に成功")

# ハミルトニアンの定義
Jz = qt.jmat(1, 'z')
H = 2 * np.pi * Jz
print("✓ ハミルトニアンの作成に成功")

# 初期状態
psi0 = qt.basis(3, 0)  # |m=+1⟩状態
print("✓ 初期状態の作成に成功")

# 短時間のシミュレーション
times = np.linspace(0, 0.1, 10)
result = simulator.simulate(H, psi0, times)
print("✓ シミュレーションの実行に成功")

print(f"\n期待値の形状: {result['expect'].shape}")
print(f"ポピュレーションの形状: {result['populations'].shape}")
print("\n全ての検証テストに合格しました！✓")
```

### テストスイートの実行（開発者向け）

開発版を使用している場合、ユニットテストを実行できます：

```bash
# quditディレクトリにテストがある場合
cd qudit
pytest -v

# または特定のテストファイルを実行
pytest tests/test_spin1_encoding.py -v
```

## クイックスタート

インストールが完了したら、以下の簡単な例でスピンS=1のシミュレーションを実行できます。

### 例1: 基本的なゼーマン効果のシミュレーション

```python
import numpy as np
import qutip as qt
from qudit.qubit import StatevectorSimulator

# パラメータ設定
omega0 = 2 * np.pi * 1.0  # 周波数（GHz）
times = np.linspace(0, 2.0, 100)  # 時間配列（μs）

# ハミルトニアン: H = -ω₀ Jz
Jz = qt.jmat(1, 'z')
H = -omega0 * Jz

# 初期状態: スピンコヒーレント状態
psi0 = qt.spin_coherent(1, np.pi/2, 0)

# シミュレータの初期化（2次トロッター分解）
simulator = StatevectorSimulator(trotter_order=2)

# シミュレーション実行
result = simulator.simulate(H, psi0, times)

# 結果の表示
print(f"計算完了: {len(times)} 時刻点")
print(f"最終時刻でのポピュレーション:")
print(f"  P(m=+1) = {result['populations'][-1, 0]:.4f}")
print(f"  P(m= 0) = {result['populations'][-1, 1]:.4f}")
print(f"  P(m=-1) = {result['populations'][-1, 2]:.4f}")
```

### 例2: 厳密解との比較

```python
# 上記の続き
comparison = simulator.compare_with_exact(H, psi0, times)

print(f"\n精度評価:")
print(f"  最大期待値誤差: {comparison['errors']['max_expect_error']:.2e}")
print(f"  平均期待値誤差: {comparison['errors']['mean_expect_error']:.2e}")
print(f"  最大ポピュレーション誤差: {comparison['errors']['max_pop_error']:.2e}")
```

### 例3: 量子回路の可視化

```python
import matplotlib.pyplot as plt

# 回路の可視化
fig, ax, circuit = simulator.visualize_circuit(
    H, 
    times[:10],  # 最初の10ステップ
    title="量子回路: ゼーマン効果"
)

print(f"ゲート数: {len(circuit.gates)}")
print(f"回路の深さ: {circuit.depth()}")

plt.tight_layout()
plt.show()
```

### より詳細な例

チュートリアルノートブックには、より高度な使用例が含まれています：

```bash
cd qudit/tutorials
jupyter notebook spin1_qubit_simulation.ipynb
```

チュートリアルの内容：
- スピンS=1の基礎理論
- 各種ハミルトニアンのシミュレーション
- トロッター分解の精度比較
- 量子回路の可視化
- 性能評価とベンチマーク

## トラブルシューティング

### よくある問題と解決方法

#### 問題1: `ModuleNotFoundError: No module named 'qudit'`

**原因**: `qudit` モジュールがPythonパスに含まれていない。

**解決方法**:
```python
import sys
sys.path.insert(0, '/path/to/qutip')  # qutipリポジトリのルートパス
from qudit.qubit import StatevectorSimulator
```

または、環境変数 `PYTHONPATH` を設定：
```bash
export PYTHONPATH="/path/to/qutip:$PYTHONPATH"
```

#### 問題2: `ImportError: cannot import name 'StatevectorSimulator'`

**原因**: QuTiPが正しくインストールされていない、または古いバージョン。

**解決方法**:
```bash
# QuTiPを最新版に更新
pip install --upgrade qutip

# または開発版を再インストール
cd /path/to/qutip
python setup.py develop
```

#### 問題3: Cython関連のエラー

**原因**: QuTiPのCython拡張モジュールがビルドされていない。

**解決方法**:
```bash
# 必要なビルドツールをインストール
pip install cython numpy scipy setuptools wheel

# QuTiPを再ビルド
cd /path/to/qutip
python setup.py build_ext --inplace
```

#### 問題4: 数値精度の問題

**症状**: シミュレーション結果が期待と大きく異なる。

**解決方法**:
1. トロッター分解の次数を上げる：
```python
simulator = StatevectorSimulator(trotter_order=4)
```

2. 時間ステップを細かくする：
```python
times = np.linspace(0, 2.0, 1000)  # より多くの時刻点
```

3. 厳密解と比較して誤差を確認：
```python
comparison = simulator.compare_with_exact(H, psi0, times)
print(comparison['errors'])
```

#### 問題5: matplotlib関連のエラー

**症状**: 回路可視化で `ImportError: No module named 'matplotlib'`

**解決方法**:
```bash
pip install matplotlib
```

#### 問題6: Jupyter Notebookでインポートできない

**原因**: ノートブックのカーネルが正しい仮想環境を使用していない。

**解決方法**:
```bash
# 仮想環境にipykernelをインストール
source qutip-env/bin/activate  # 仮想環境を有効化
pip install ipykernel

# カーネルを登録
python -m ipykernel install --user --name=qutip-env --display-name="Python (qutip)"

# Jupyter Notebookでカーネルを選択: Kernel > Change kernel > Python (qutip)
```

### デバッグのヒント

1. **バージョン確認**:
```python
import qutip as qt
import numpy as np
import scipy
print(f"QuTiP: {qt.__version__}")
print(f"NumPy: {np.__version__}")
print(f"SciPy: {scipy.__version__}")
```

2. **Pythonパスの確認**:
```python
import sys
print('\n'.join(sys.path))
```

3. **モジュールの場所を確認**:
```python
import qudit
print(qudit.__file__)  # エラーの場合は存在しない
```

### サポート

問題が解決しない場合：

1. **GitHubのIssues**: https://github.com/qutip/qutip/issues
2. **QuTiP Discussions**: https://github.com/qutip/qutip/discussions
3. **QuTiP Google Group**: qutip@googlegroups.com

問題を報告する際は、以下の情報を含めてください：
- 使用しているOS（Windows/Linux/macOS）
- Pythonのバージョン
- QuTiPのバージョン
- エラーメッセージの全文
- 実行したコードの最小再現例

## アンインストール

### 開発モードでインストールした場合

```bash
cd /path/to/qutip
python setup.py develop --uninstall
```

または：

```bash
pip uninstall qutip
```

### 仮想環境ごと削除する場合

```bash
# 仮想環境を無効化
deactivate

# ディレクトリを削除
rm -rf qutip-env/
```

### Pythonパスの設定を削除

環境変数やスクリプトから `PYTHONPATH` の設定を削除してください。

## その他のリソース

### ドキュメント

- [README.md](./README.md) - quditモジュールの概要
- [spin1_quantum_dynamics.md](./spin1_quantum_dynamics.md) - スピンS=1の量子ダイナミクスの理論
- [qubit/README.md](../qubit/README.md) - 量子ビットアルゴリズムの詳細
- [qubit/CIRCUIT_VISUALIZATION.md](../qubit/CIRCUIT_VISUALIZATION.md) - 回路可視化機能の説明

### チュートリアル

- [tutorials/spin1_qubit_simulation.ipynb](../tutorials/spin1_qubit_simulation.ipynb) - 実践的なチュートリアル

### QuTiP公式リソース

- **公式サイト**: https://qutip.org/
- **ドキュメント**: https://qutip.readthedocs.io/
- **チュートリアル**: https://github.com/qutip/qutip-tutorials
- **論文**: [QuTiP 2: A Python framework for the dynamics of open quantum systems](https://www.sciencedirect.com/science/article/pii/S0010465512003955)

## ライセンス

このモジュールは、QuTiPプロジェクトの一部として、BSD 3-Clause Licenseの下で配布されています。詳細は、リポジトリルートの `LICENSE.txt` を参照してください。

---

**最終更新**: 2024年10月
**作成者**: QuTiP Development Team
