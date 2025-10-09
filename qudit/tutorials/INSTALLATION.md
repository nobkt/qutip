# インストールガイド - Qudit Tutorials

このドキュメントでは、Quditチュートリアルを実行するために必要なパッケージのインストール方法を説明します。

## 必須パッケージ

すべてのチュートリアルで必要なパッケージ：

```bash
pip install numpy scipy matplotlib qutip jupyter
```

個別にインストールする場合：

```bash
pip install numpy>=1.22
pip install scipy>=1.8
pip install matplotlib>=3.5
pip install qutip>=5.0
pip install jupyter
```

## オプショナルパッケージ

### Qiskitシミュレーション用

`zeeman_effect_comprehensive.ipynb`でQiskitベースのシミュレーション（方法3-5）を実行する場合：

```bash
pip install qiskit qiskit-aer
```

または最新版：

```bash
pip install qiskit>=1.0
pip install qiskit-aer>=0.13
```

### MQT Quditsシミュレーション用

`zeeman_effect_comprehensive.ipynb`および`spin1_qudit_dynamics.ipynb`でMQTベースのシミュレーション（方法6-8）を実行する場合：

```bash
pip install mqt.qudits
```

または最新版：

```bash
pip install mqt.qudits>=1.0
```

**注意**: MQT Quditsは比較的新しいパッケージで、一部の環境ではインストールに失敗する可能性があります。

## すべてのパッケージを一度にインストール

すべての機能を使用する場合（推奨）：

```bash
pip install numpy scipy matplotlib qutip jupyter qiskit qiskit-aer mqt.qudits
```

## 仮想環境の使用（推奨）

システムのPython環境を汚染しないように、仮想環境の使用を推奨します：

### venvの使用

```bash
# 仮想環境の作成
python -m venv qutip-env

# 仮想環境の有効化（Linux/Mac）
source qutip-env/bin/activate

# 仮想環境の有効化（Windows）
qutip-env\Scripts\activate

# パッケージのインストール
pip install numpy scipy matplotlib qutip jupyter qiskit qiskit-aer mqt.qudits
```

### Condaの使用

```bash
# 新しい環境の作成
conda create -n qutip-env python=3.10

# 環境の有効化
conda activate qutip-env

# パッケージのインストール
conda install -c conda-forge numpy scipy matplotlib jupyter
pip install qutip qiskit qiskit-aer mqt.qudits
```

## インストールの確認

インストールが成功したことを確認するには、以下のPythonスクリプトを実行してください：

```python
import sys

def check_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {package_name}: {version}")
        return True
    except ImportError:
        print(f"✗ {package_name}: NOT INSTALLED")
        return False

print("Checking required packages...")
print("=" * 60)

# Required packages
required = [
    ('NumPy', 'numpy'),
    ('SciPy', 'scipy'),
    ('Matplotlib', 'matplotlib'),
    ('QuTiP', 'qutip'),
]

print("\nRequired:")
all_required = all(check_package(name, imp) for name, imp in required)

# Optional packages
print("\nOptional (Qiskit):")
qiskit_available = check_package('Qiskit', 'qiskit')
qiskit_aer_available = check_package('Qiskit-Aer', 'qiskit_aer')

print("\nOptional (MQT):")
mqt_available = check_package('MQT Qudits', 'mqt.qudits')

print("\n" + "=" * 60)
if all_required:
    print("✓ All required packages are installed!")
    if qiskit_available and qiskit_aer_available:
        print("✓ Qiskit packages are installed (methods 3-5 available)")
    else:
        print("⚠ Qiskit not available (methods 3-5 will be skipped)")
    
    if mqt_available:
        print("✓ MQT Qudits is installed (methods 6-8 available)")
    else:
        print("⚠ MQT Qudits not available (methods 6-8 will be skipped)")
else:
    print("✗ Some required packages are missing!")
    print("Please install them with: pip install numpy scipy matplotlib qutip jupyter")
```

このスクリプトを`check_installation.py`として保存し、実行してください：

```bash
python check_installation.py
```

## トラブルシューティング

### QuTiPのインポートエラー

```
ModuleNotFoundError: No module named 'qutip'
```

**解決方法**:
```bash
pip install qutip
```

### Qiskitのバージョン互換性

古いバージョンのQiskitがインストールされている場合、アップグレードしてください：

```bash
pip install --upgrade qiskit qiskit-aer
```

### MQT Quditsのインストールエラー

MQT Quditsのインストールに失敗する場合、以下を試してください：

1. Pythonのバージョンを確認（3.8以上が推奨）
2. pipを最新版にアップグレード：
   ```bash
   pip install --upgrade pip
   ```
3. 開発版のインストール：
   ```bash
   pip install git+https://github.com/cda-tum/mqt-qudits.git
   ```

### Jupyter Notebookが起動しない

```bash
pip install --upgrade jupyter notebook
```

### メモリ不足エラー

ノートブックの実行中にメモリ不足エラーが発生する場合：

1. 時間ステップ数を減らす
2. ショット数を減らす
3. 測定点を減らす

例：
```python
# 元の設定
times = np.linspace(0, 3.0, 100)  # 100点
n_shots = 10000

# メモリを節約する設定
times = np.linspace(0, 3.0, 50)   # 50点に削減
n_shots = 5000                     # 5000に削減
```

## システム要件

- Python 3.8以上（3.10以上を推奨）
- RAM: 最低4GB、推奨8GB以上
- ディスク空間: 最低500MB（パッケージとデータ用）

## サポート

問題が解決しない場合は、以下をお試しください：

1. QuTiPの公式ドキュメント: https://qutip.org/docs/latest/
2. Qiskitの公式ドキュメント: https://qiskit.org/documentation/
3. MQT Quditsのドキュメント: https://github.com/cda-tum/mqt-qudits
4. GitHubのIssue: https://github.com/nobkt/qutip/issues

---

最終更新: 2024年
