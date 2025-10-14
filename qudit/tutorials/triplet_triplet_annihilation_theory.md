# 三重項-三重項消滅(TTA)過程の量子ダイナミクス理論（3分子線形系）

## 目次

1. [はじめに](#はじめに)
2. [分子の電子状態](#分子の電子状態)
3. [古典的な速度論モデル](#古典的な速度論モデル)
4. [量子力学的記述](#量子力学的記述)
5. [Qubit表現](#qubit表現)
6. [Qudit表現](#qudit表現)
7. [鈴木-トロッター分解](#鈴木-トロッター分解)
8. [量子回路実装](#量子回路実装)

---

## 1. はじめに

三重項-三重項消滅(Triplet-Triplet Annihilation, TTA)は、二つの励起三重項状態の分子が相互作用し、一方が励起一重項状態に、他方が基底一重項状態に遷移する過程です。この過程は、アップコンバージョン発光、太陽電池、有機ELなど、様々な光電子デバイスにおいて重要な役割を果たします。

### 1.1 物理的背景

色素分子は以下の電子状態を持ちます：

- **基底一重項状態 (S₀)**: 全電子がスピン対を形成し、全スピン角運動量が0
- **励起一重項状態 (S₁)**: 電子が励起されているが、スピン対が保たれている
- **励起三重項状態 (T₁)**: 二つの不対電子が平行スピンを持ち、全スピン角運動量が1

### 1.2 研究対象のプロセス

本研究では、直線状に配列された三つの色素分子A、B、Cを含む系において以下の過程を考察します：

1. **励起エネルギー移動**: 隣接分子間でのみ起こる（A-B間、B-C間）
2. **三重項-三重項消滅**: 隣接分子間でのみ起こる（A-B間、B-C間）

### 1.3 線形配列と最近接相互作用

分子は以下のように直線状に配列されています：

```
A ⟷ B ⟷ C
```

- エネルギー移動とTTAは隣接分子間（A-B間、B-C間）でのみ起こります
- A-C間の直接相互作用は存在しません
- 初期状態：両端の分子（AとC）が励起三重項状態、中心の分子（B）が基底一重項状態

---

## 2. 分子の電子状態

### 2.1 状態の定義

各分子は3つの電子状態を持ちます：

$$
\begin{aligned}
|S_0\rangle &: \text{基底一重項状態} \\
|T_1\rangle &: \text{励起三重項状態} \\
|S_1\rangle &: \text{励起一重項状態}
\end{aligned}
$$

### 2.2 エネルギー準位

一般に、エネルギー順位は以下の通りです：

$$
E_{S_0} < E_{T_1} < E_{S_1}
$$

典型的なエネルギー差：
- $E_{T_1} - E_{S_0} \sim 1.5 \text{ eV}$
- $E_{S_1} - E_{T_1} \sim 0.5 \text{ eV}$

### 2.3 スピン多重度

- **一重項状態**: $S = 0$、$2S+1 = 1$
- **三重項状態**: $S = 1$、$2S+1 = 3$

---

## 3. 古典的な速度論モデル

### 3.1 速度方程式

3分子線形系(A-B-C)のポピュレーション動力学は以下の速度方程式で記述されます。エネルギー移動は可逆的ですが、TTAは非可逆的な過程です：

$$
\begin{aligned}
\frac{d[A_{S_0}]}{dt} &= -k_{\text{ET}}[A_{S_0}][B_{T_1}] + k_{\text{ET}}[A_{T_1}][B_{S_0}] + k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[A_{T_1}]}{dt} &= k_{\text{ET}}[A_{S_0}][B_{T_1}] - k_{\text{ET}}[A_{T_1}][B_{S_0}] - 2k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[A_{S_1}]}{dt} &= k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[B_{S_0}]}{dt} &= k_{\text{ET}}[A_{T_1}][B_{S_0}] - k_{\text{ET}}[A_{S_0}][B_{T_1}] + k_{\text{ET}}[C_{T_1}][B_{S_0}] - k_{\text{ET}}[B_{S_0}][C_{T_1}] \\
&\quad + k_{\text{TTA}}[A_{T_1}][B_{T_1}] + k_{\text{TTA}}[B_{T_1}][C_{T_1}] \\
\frac{d[B_{T_1}]}{dt} &= k_{\text{ET}}[A_{S_0}][B_{T_1}] - k_{\text{ET}}[A_{T_1}][B_{S_0}] + k_{\text{ET}}[C_{S_0}][B_{T_1}] - k_{\text{ET}}[B_{T_1}][C_{S_0}] \\
&\quad - 2k_{\text{TTA}}[A_{T_1}][B_{T_1}] - 2k_{\text{TTA}}[B_{T_1}][C_{T_1}] \\
\frac{d[B_{S_1}]}{dt} &= k_{\text{TTA}}[A_{T_1}][B_{T_1}] + k_{\text{TTA}}[B_{T_1}][C_{T_1}] \\
\frac{d[C_{S_0}]}{dt} &= -k_{\text{ET}}[C_{S_0}][B_{T_1}] + k_{\text{ET}}[C_{T_1}][B_{S_0}] + k_{\text{TTA}}[C_{T_1}][B_{T_1}] \\
\frac{d[C_{T_1}]}{dt} &= k_{\text{ET}}[C_{S_0}][B_{T_1}] - k_{\text{ET}}[C_{T_1}][B_{S_0}] - 2k_{\text{TTA}}[C_{T_1}][B_{T_1}] \\
\frac{d[C_{S_1}]}{dt} &= k_{\text{TTA}}[C_{T_1}][B_{T_1}]
\end{aligned}
$$

ここで：
- $k_{\text{ET}}$: エネルギー移動速度定数（隣接分子間、可逆的）
- $k_{\text{TTA}}$: 三重項-三重項消滅速度定数（隣接分子間、非可逆的）
- $[X_Y]$: 分子Xの状態Yのポピュレーション

**重要**: TTA項には逆反応がないため、S₁状態からT₁状態への遷移項は存在しません。これは物理的に正しい記述です。

### 3.2 初期条件

初期状態は両端の分子（AとC）が励起三重項状態、中心の分子（B）が基底一重項状態：

$$
\begin{aligned}
[A_{T_1}](0) &= 1, \quad [A_{S_0}](0) = 0, \quad [A_{S_1}](0) = 0 \\
[B_{S_0}](0) &= 1, \quad [B_{T_1}](0) = 0, \quad [B_{S_1}](0) = 0 \\
[C_{T_1}](0) &= 1, \quad [C_{S_0}](0) = 0, \quad [C_{S_1}](0) = 0
\end{aligned}
$$

### 3.3 保存則

各分子の全ポピュレーションは保存されます：

$$
[A_{S_0}] + [A_{T_1}] + [A_{S_1}] = 1
$$
$$
[B_{S_0}] + [B_{T_1}] + [B_{S_1}] = 1
$$
$$
[C_{S_0}] + [C_{T_1}] + [C_{S_1}] = 1
$$

---

## 4. 量子力学的記述

### 4.1 状態空間

3分子線形系の全状態空間は、各分子の状態空間のテンソル積です：

$$
\mathcal{H}_{\text{total}} = \mathcal{H}_A \otimes \mathcal{H}_B \otimes \mathcal{H}_C
$$

各分子の状態空間は3次元：

$$
\mathcal{H}_A = \mathcal{H}_B = \mathcal{H}_C = \text{span}\{|S_0\rangle, |T_1\rangle, |S_1\rangle\}
$$

全状態空間の次元は $3 \times 3 \times 3 = 27$ です。

### 4.2 基底状態

3分子系の計算基底は以下の27状態です。状態を $|abc\rangle$ と表記します（a, b, c ∈ {S₀, T₁, S₁}）：

$$
\begin{aligned}
&|S_0 S_0 S_0\rangle, |S_0 S_0 T_1\rangle, |S_0 S_0 S_1\rangle, \\
&|S_0 T_1 S_0\rangle, |S_0 T_1 T_1\rangle, |S_0 T_1 S_1\rangle, \\
&|S_0 S_1 S_0\rangle, |S_0 S_1 T_1\rangle, |S_0 S_1 S_1\rangle, \\
&|T_1 S_0 S_0\rangle, |T_1 S_0 T_1\rangle, |T_1 S_0 S_1\rangle, \\
&|T_1 T_1 S_0\rangle, |T_1 T_1 T_1\rangle, |T_1 T_1 S_1\rangle, \\
&|T_1 S_1 S_0\rangle, |T_1 S_1 T_1\rangle, |T_1 S_1 S_1\rangle, \\
&|S_1 S_0 S_0\rangle, |S_1 S_0 T_1\rangle, |S_1 S_0 S_1\rangle, \\
&|S_1 T_1 S_0\rangle, |S_1 T_1 T_1\rangle, |S_1 T_1 S_1\rangle, \\
&|S_1 S_1 S_0\rangle, |S_1 S_1 T_1\rangle, |S_1 S_1 S_1\rangle
\end{aligned}
$$

### 4.3 ハミルトニアンとリンドブラッド演算子

系は可逆的なコヒーレント項（ハミルトニアン）と非可逆な散逸項（リンドブラッド演算子）で記述されます。

**ハミルトニアン**（可逆的過程のみ）：

$$
H = H_0 + H_{\text{ET}}^{AB} + H_{\text{ET}}^{BC}
$$

**リンドブラッド崩壊演算子**（非可逆的TTA過程）：

$$
\{L_{\text{TTA}}^{AB,1}, L_{\text{TTA}}^{AB,2}, L_{\text{TTA}}^{BC,1}, L_{\text{TTA}}^{BC,2}\}
$$

ここで上付き文字は相互作用する分子対を示します（AB: A-B間、BC: B-C間）。

#### 4.3.1 自由ハミルトニアン

各分子の自由ハミルトニアンは対角的です：

$$
H_0 = H_A \otimes I_B \otimes I_C + I_A \otimes H_B \otimes I_C + I_A \otimes I_B \otimes H_C
$$

ここで：

$$
H_A = H_B = H_C = \begin{pmatrix}
0 & 0 & 0 \\
0 & E_T & 0 \\
0 & 0 & E_S
\end{pmatrix}
$$

ここで、$E_T = E_{T_1}$、$E_S = E_{S_1}$ です。

#### 4.3.2 エネルギー移動ハミルトニアン

エネルギー移動過程は隣接分子間でのみ起こります：

**A-B間のエネルギー移動**:

$$
|T_1 S_0 *\rangle \leftrightarrow |S_0 T_1 *\rangle
$$

ハミルトニアンは：

$$
H_{\text{ET}}^{AB} = V_{\text{ET}} \sum_c (|T_1 S_0 c\rangle\langle S_0 T_1 c| + |S_0 T_1 c\rangle\langle T_1 S_0 c|)
$$

ここで $c$ は分子Cの任意の状態（$S_0, T_1, S_1$）を表します。

**B-C間のエネルギー移動**:

$$
|* S_0 T_1\rangle \leftrightarrow |* T_1 S_0\rangle
$$

ハミルトニアンは：

$$
H_{\text{ET}}^{BC} = V_{\text{ET}} \sum_a (|a S_0 T_1\rangle\langle a T_1 S_0| + |a T_1 S_0\rangle\langle a S_0 T_1|)
$$

ここで $a$ は分子Aの任意の状態を表します。

#### 4.3.3 三重項-三重項消滅（非可逆過程）

**重要**: TTA過程は非可逆な過程であり、逆反応（S₁S₀ → T₁T₁）は物理的に起こりません。エネルギー保存則により、2つの三重項状態（合計エネルギー 2E_T1）が1つの一重項励起状態（E_S1）と1つの基底状態（E_S0 = 0）に変換され、差分エネルギーが熱として放出されます。

TTA過程は隣接分子間でのみ起こる非可逆な遷移です：

**A-B間のTTA**:

$$
|T_1 T_1 *\rangle \rightarrow |S_1 S_0 *\rangle \text{ または } |S_0 S_1 *\rangle
$$

この非可逆過程をリンドブラッド形式で記述します。Lindblad崩壊演算子：

$$
L_{\text{TTA}}^{AB,1} = \sqrt{\gamma_{\text{TTA}}} \sum_c |S_1 S_0 c\rangle\langle T_1 T_1 c|
$$

$$
L_{\text{TTA}}^{AB,2} = \sqrt{\gamma_{\text{TTA}}} \sum_c |S_0 S_1 c\rangle\langle T_1 T_1 c|
$$

**B-C間のTTA**:

$$
|* T_1 T_1\rangle \rightarrow |* S_1 S_0\rangle \text{ または } |* S_0 S_1\rangle
$$

Lindblad崩壊演算子：

$$
L_{\text{TTA}}^{BC,1} = \sqrt{\gamma_{\text{TTA}}} \sum_a |a S_1 S_0\rangle\langle a T_1 T_1|
$$

$$
L_{\text{TTA}}^{BC,2} = \sqrt{\gamma_{\text{TTA}}} \sum_a |a S_0 S_1\rangle\langle a T_1 T_1|
$$

ここで、$\gamma_{\text{TTA}}$ はTTA過程の速度定数です。

### 4.4 時間発展

TTA過程の非可逆性を正しく扱うため、Lindbladマスター方程式を使用します：

$$
\frac{d\rho}{dt} = -\frac{i}{\hbar}[H, \rho] + \sum_k \left(L_k \rho L_k^\dagger - \frac{1}{2}\{L_k^\dagger L_k, \rho\}\right)
$$

ここで：
- $H = H_0 + H_{\text{ET}}^{AB} + H_{\text{ET}}^{BC}$ （エネルギー移動のみを含むハミルトニアン）
- $L_k$ はリンドブラッド崩壊演算子（TTA過程を記述）
- $\rho$ は密度演算子
- $\{\cdot, \cdot\}$ は反交換子

第一項はユニタリ時間発展（可逆的エネルギー移動）を記述し、第二項は非可逆なTTA過程を記述します。

初期状態が純粋状態 $|\psi(0)\rangle$ の場合：

$$
\rho(0) = |\psi(0)\rangle\langle\psi(0)|
$$

時間発展により、系は一般に混合状態となります。

### 4.5 初期状態

初期状態は両端が励起三重項、中心が基底一重項：

$$
|\psi(0)\rangle = |T_1 S_0 T_1\rangle
$$

### 4.6 観測量

各状態のポピュレーションは射影演算子で測定されます：

$$
P_{abc} = |abc\rangle\langle abc|
$$

ポピュレーション：

$$
p_{abc}(t) = \langle\psi(t)|P_{abc}|\psi(t)\rangle = |\langle abc|\psi(t)\rangle|^2
$$

$$
P_{XY} = |X Y\rangle\langle X Y|
$$

ポピュレーション：

$$
p_{XY}(t) = \langle\psi(t)|P_{XY}|\psi(t)\rangle = |\langle X Y|\psi(t)\rangle|^2
$$

---

## 5. Qubit表現

### 5.1 状態の符号化

3準位系を2量子ビットで符号化します：

$$
\begin{aligned}
|S_0\rangle &\rightarrow |00\rangle \\
|T_1\rangle &\rightarrow |01\rangle \\
|S_1\rangle &\rightarrow |10\rangle \\
&\quad |11\rangle \text{ (未使用)}
\end{aligned}
$$

### 5.2 3分子系の符号化

3分子線形系は6量子ビットで表現されます（各分子に2量子ビット）：

- 分子A: qubits 0-1
- 分子B: qubits 2-3
- 分子C: qubits 4-5

$$
|X_A X_B X_C\rangle \rightarrow |\text{code}(X_A)\rangle \otimes |\text{code}(X_B)\rangle \otimes |\text{code}(X_C)\rangle
$$

全状態空間の次元: $2^6 = 64$ （うち27状態のみ物理的）

### 5.3 初期状態

初期状態 $|T_1 S_0 T_1\rangle$ は：

$$
|T_1 S_0 T_1\rangle \rightarrow |01\rangle \otimes |00\rangle \otimes |01\rangle = |010001\rangle
$$

10進数表現: $0 \cdot 32 + 1 \cdot 16 + 0 \cdot 8 + 0 \cdot 4 + 0 \cdot 2 + 1 \cdot 1 = 17$

### 5.4 重要な状態の符号化例

$$
\begin{aligned}
|T_1 S_0 T_1\rangle &\rightarrow |010001\rangle = |17\rangle_{10} \\
|S_0 T_1 T_1\rangle &\rightarrow |000101\rangle = |5\rangle_{10} \\
|T_1 T_1 S_0\rangle &\rightarrow |010100\rangle = |20\rangle_{10} \\
|S_1 S_0 T_1\rangle &\rightarrow |100001\rangle = |33\rangle_{10} \\
|T_1 S_0 S_1\rangle &\rightarrow |010010\rangle = |18\rangle_{10}
\end{aligned}
$$

### 5.5 パウリ演算子による演算子の構成

#### 5.5.1 基本演算子

単一量子ビットのパウリ演算子：

$$
\begin{aligned}
\sigma_x &= \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad
\sigma_y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad
\sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} \\
I &= \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}
\end{aligned}
$$

#### 5.5.2 射影演算子

状態 $|ij\rangle$ への射影演算子：

$$
P_{ij} = |ij\rangle\langle ij| = \frac{1}{4}(I + (-1)^i\sigma_z) \otimes (I + (-1)^j\sigma_z)
$$

#### 5.3.3 エネルギー移動演算子

$$
|01\rangle|00\rangle \leftrightarrow |00\rangle|01\rangle
$$

この遷移は以下のパウリ演算子の組み合わせで表現できます：

$$
H_{\text{ET}}^{\text{qubit}} = \frac{V_{\text{ET}}}{4}(\sigma_x^{(1)} \otimes \sigma_x^{(2)} \otimes I^{(3)} \otimes \sigma_x^{(4)})
$$

ここで、上付き文字は量子ビットのインデックスを示します。

#### 5.3.4 TTA演算子

$$
|01\rangle|01\rangle \leftrightarrow |10\rangle|00\rangle + |00\rangle|10\rangle
$$

この演算子の構成はより複雑で、複数のパウリ演算子の組み合わせが必要です。

### 5.4 量子回路による実装

#### 5.4.1 状態準備

初期状態 $|T_1 S_0\rangle \rightarrow |0100\rangle$ の準備：

1. 全量子ビットを $|0\rangle$ で初期化
2. 量子ビット1にXゲートを適用: $|0000\rangle \rightarrow |0100\rangle$

#### 5.4.2 時間発展

時間発展演算子 $U(t) = e^{-iHt}$ を鈴木-トロッター分解で近似します（詳細は第7節参照）。

#### 5.4.3 測定

各基底状態のポピュレーションを測定するために、計算基底で測定を行います。

---

## 6. Qudit表現

### 6.1 Qutrit（3準位量子系）

Quditは $d$ 準位量子系です。3準位の場合、qutritと呼ばれます。

### 6.2 状態の直接表現

3準位系を直接3準位quditで表現します：

$$
\begin{aligned}
|S_0\rangle &\rightarrow |0\rangle_3 \\
|T_1\rangle &\rightarrow |1\rangle_3 \\
|S_1\rangle &\rightarrow |2\rangle_3
\end{aligned}
$$

### 6.3 3分子系の表現

3分子線形系は3つのqutritで表現されます：

$$
|X_A X_B X_C\rangle \rightarrow |i\rangle_3 \otimes |j\rangle_3 \otimes |k\rangle_3
$$

全状態空間の次元は $3 \times 3 \times 3 = 27$ です。これはqubit表現の64次元に比べて大幅にコンパクトです。

### 6.4 初期状態

初期状態 $|T_1 S_0 T_1\rangle$ は：

$$
|T_1 S_0 T_1\rangle \rightarrow |1\rangle_3 \otimes |0\rangle_3 \otimes |1\rangle_3 = |101\rangle_3
$$

3進数表現: $1 \cdot 9 + 0 \cdot 3 + 1 \cdot 1 = 10$ （10進数）

### 6.5 演算子の表現

#### 6.5.1 Gell-Mann行列

3準位系の演算子は8つのGell-Mann行列 $\{\lambda_1, \ldots, \lambda_8\}$ と恒等行列で表現できます。

$$
\lambda_1 = \begin{pmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}, \quad
\lambda_2 = \begin{pmatrix} 0 & -i & 0 \\ i & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}, \quad
\lambda_3 = \begin{pmatrix} 1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 0 \end{pmatrix}
$$

$$
\lambda_4 = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 0 & 0 \\ 1 & 0 & 0 \end{pmatrix}, \quad
\lambda_5 = \begin{pmatrix} 0 & 0 & -i \\ 0 & 0 & 0 \\ i & 0 & 0 \end{pmatrix}, \quad
\lambda_6 = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & 1 \\ 0 & 1 & 0 \end{pmatrix}
$$

$$
\lambda_7 = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & -i \\ 0 & i & 0 \end{pmatrix}, \quad
\lambda_8 = \frac{1}{\sqrt{3}}\begin{pmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & -2 \end{pmatrix}
$$

#### 6.5.2 昇降演算子

$$
\begin{aligned}
X_{01} &= |0\rangle\langle 1| + |1\rangle\langle 0| = \frac{1}{2}(\lambda_1 + i\lambda_2) \\
X_{12} &= |1\rangle\langle 2| + |2\rangle\langle 1| = \frac{1}{2}(\lambda_6 + i\lambda_7) \\
X_{02} &= |0\rangle\langle 2| + |2\rangle\langle 0| = \frac{1}{2}(\lambda_4 + i\lambda_5)
\end{aligned}
$$

### 6.5 量子回路による実装

#### 6.5.1 Qudit回路

Quditゲートは3準位系に作用する一般的なユニタリ演算子です：

$$
U \in SU(3)
$$

#### 6.5.2 基本ゲート

- **Xゲート**: $|0\rangle \leftrightarrow |1\rangle$
- **X₁₂ゲート**: $|1\rangle \leftrightarrow |2\rangle$
- **X₀₂ゲート**: $|0\rangle \leftrightarrow |2\rangle$
- **位相ゲート**: 対角ユニタリ演算子

#### 6.5.3 2-quditゲート

2つのqutrit間の相互作用を表現するゲート：

$$
U_{AB} \in SU(9)
$$

---

## 7. 鈴木-トロッター分解

### 7.1 基本原理

ハミルトニアンが和の形で表される場合：

$$
H = H_0 + H_{\text{ET}}^{AB} + H_{\text{ET}}^{BC} + H_{\text{TTA}}^{AB} + H_{\text{TTA}}^{BC}
$$

時間発展演算子は：

$$
U(t) = e^{-iHt}
$$

一般に、各項は可換ではない（$[H_i, H_j] \neq 0$）ため、この指数関数を単純に分解できません。

### 7.2 1次トロッター分解（Lie-Trotter公式）

$$
e^{-i(H_1 + H_2)t} \approx e^{-iH_1 t} e^{-iH_2 t} + O(t^2)
$$

より一般的に：

$$
e^{-iHt} \approx \left(e^{-iH_1\Delta t} e^{-iH_2\Delta t} \cdots e^{-iH_n\Delta t}\right)^{N} + O(\Delta t^2)
$$

ここで、$t = N\Delta t$ です。

### 7.3 2次トロッター分解（Strang分割）

$$
e^{-i(H_1 + H_2)t} \approx e^{-iH_1 t/2} e^{-iH_2 t} e^{-iH_1 t/2} + O(t^3)
$$

より対称的な形式：

$$
e^{-iHt} \approx \left(e^{-iH_1\Delta t/2} e^{-iH_2\Delta t/2} \cdots e^{-iH_n\Delta t/2} e^{-iH_n\Delta t/2} \cdots e^{-iH_2\Delta t/2} e^{-iH_1\Delta t/2}\right)^{N} + O(\Delta t^3)
$$

### 7.4 4次トロッター分解（鈴木のフラクタル分解）

4次の精度を達成するために、鈴木の方法を使用します：

$$
U_4(\Delta t) = U_2(p\Delta t)^2 U_2((1-4p)\Delta t) U_2(p\Delta t)^2
$$

ここで：

$$
p = \frac{1}{4 - 4^{1/3}} = \frac{1}{2(2 - 2^{1/3})}
$$

誤差は $O(\Delta t^5)$ です。

### 7.5 本問題への適用（Lindbladマスター方程式）

我々の3分子線形系では、可逆的な項（ハミルトニアン）と非可逆的な項（リンドブラッド演算子）を別々に扱います：

**ハミルトニアン**（可逆的過程）:

$$
H = H_0 + H_{\text{ET}}^{AB} + H_{\text{ET}}^{BC}
$$

**リンドブラッド崩壊演算子**（非可逆的TTA過程）:

$$
\{L_{\text{TTA}}^{AB,1}, L_{\text{TTA}}^{AB,2}, L_{\text{TTA}}^{BC,1}, L_{\text{TTA}}^{BC,2}\}
$$

Lindbladマスター方程式の時間発展は、ユニタリ部分と非ユニタリ部分に分けて考えます：

$$
\frac{d\rho}{dt} = -\frac{i}{\hbar}[H, \rho] + \mathcal{D}[\{L_k\}]\rho
$$

ここで、$\mathcal{D}[\{L_k\}]\rho = \sum_k (L_k \rho L_k^\dagger - \frac{1}{2}\{L_k^\dagger L_k, \rho\})$ は散逸項です。

鈴木-トロッター分解をLindbladマスター方程式に適用する場合、ユニタリ部分（ハミルトニアン）には通常のトロッター分解を、非ユニタリ部分（リンドブラッド項）には別の近似手法を使用します。

2次分解の一例：

$$
e^{\mathcal{L}\Delta t} \approx e^{\mathcal{L}_H\Delta t/2} e^{\mathcal{D}\Delta t} e^{\mathcal{L}_H\Delta t/2}
$$

ここで、$\mathcal{L}_H\rho = -\frac{i}{\hbar}[H, \rho]$ はユニタリ部分のリウビリアンです。

さらに、ハミルトニアン部分を項ごとに分解：

$$
e^{\mathcal{L}_H\Delta t/2} \approx e^{-iH_0\Delta t/2} \cdot e^{-iH_{\text{ET}}^{AB}\Delta t/2} \cdot e^{-iH_{\text{ET}}^{BC}\Delta t/2}
$$

**注意**: ハミルトニアンからH_TTAの項は除外されています。これらの過程は非可逆的であり、リンドブラッド演算子で正しく記述されます。

### 7.6 精度とステップ数

時間ステップ $\Delta t$ が小さいほど、精度が向上します。全時間 $T$ に対して：

$$
N = \frac{T}{\Delta t}
$$

ステップ数が多いほど、計算コストが増加しますが、精度も向上します。

### 7.7 誤差評価

$n$ 次トロッター分解の誤差：

$$
\|U_{\text{exact}}(t) - U_{\text{Trotter}}^{(n)}(t)\| = O(\Delta t^{n+1})
$$

したがって：
- 1次: $O(\Delta t^2)$
- 2次: $O(\Delta t^3)$
- 4次: $O(\Delta t^5)$

---

## 8. 量子回路実装

### 8.1 Qubit実装（Qiskit）

#### 8.1.1 回路構成

1. **初期化**: $|010001\rangle$ 状態の準備（6量子ビット）
2. **トロッター分解**: 各ハミルトニアン項を量子ゲートに分解
3. **測定**: 全量子ビットを計算基底で測定

#### 8.1.2 ゲート分解

各ハミルトニアン項 $H_i$ に対して、$e^{-iH_i\Delta t}$ をパウリゲートの組み合わせに分解します。

例：単一パウリ演算子の場合

$$
e^{-i\theta \sigma_z} = \begin{pmatrix}
e^{-i\theta} & 0 \\
0 & e^{i\theta}
\end{pmatrix} = R_z(2\theta)
$$

#### 8.1.3 回路メトリクス

- **量子ビット数**: 6（3分子 × 2量子ビット/分子）
- **ゲート数**: トロッターステップ数とハミルトニアン項の複雑さに依存
- **回路深さ**: トロッターステップ数に比例

#### 8.1.4 シミュレーション

- **Statevectorシミュレータ**: 正確な量子状態ベクトルを計算（64次元）
- **ショットシミュレータ**: 測定の統計的サンプリング（例：10000ショット）

### 8.2 Qudit実装（MQT）

#### 8.2.1 回路構成

1. **初期化**: $|101\rangle_3$ 状態の準備（分子A: $|1\rangle_3$、分子B: $|0\rangle_3$、分子C: $|1\rangle_3$）
2. **トロッター分解**: 各ハミルトニアン項をquditゲートに分解
3. **測定**: 全quditを計算基底で測定

#### 8.2.2 Quditゲート

- **単一quditゲート**: $U \in SU(3)$
- **2-quditゲート**: $U \in SU(9)$（隣接分子間の相互作用）

MQT（Munich Quantum Toolkit）は、任意の次元のquditをサポートします。

#### 8.2.3 回路メトリクス

- **Qudit数**: 3（各分子に1 qutrit）
- **ゲート数**: Qubit実装より少ない（直接3準位演算）
- **回路深さ**: Qubit実装より浅い可能性

#### 8.2.4 シミュレーション

- **Statevectorシミュレータ**: 27次元の状態ベクトルを計算
- **ショットシミュレータ**: 測定の統計的サンプリング

### 8.3 比較分析

| 項目 | Qubit (Qiskit) | Qudit (MQT) |
|------|----------------|-------------|
| 量子資源数 | 6 qubits | 3 qutrits |
| 状態空間次元 | 64 (未使用: 37) | 27 |
| ゲート数 | 多い | 少ない |
| 回路深さ | 深い | 浅い |
| 実装の複雑さ | 標準的 | 新しい技術 |
| ハードウェア対応 | 広く利用可能 | 限定的 |
| 効率性 | 64/27 ≈ 2.4倍の状態空間 | より効率的 |

---

## 9. 物理的解釈

### 9.1 エネルギー移動

初期状態 $|T_1 S_0 T_1\rangle$ から始まり、隣接分子間でエネルギー移動が起こります：

**A-B間のエネルギー移動**:
$$
|T_1 S_0 T_1\rangle \xrightarrow{H_{\text{ET}}^{AB}} \alpha|T_1 S_0 T_1\rangle + \beta|S_0 T_1 T_1\rangle
$$

**B-C間のエネルギー移動**:
$$
|T_1 S_0 T_1\rangle \xrightarrow{H_{\text{ET}}^{BC}} \gamma|T_1 S_0 T_1\rangle + \delta|T_1 T_1 S_0\rangle
$$

中心分子Bはエネルギー移動のハブとして機能します。

### 9.2 三重項-三重項消滅（非可逆過程）

隣接分子間で両方が三重項状態にある場合、非可逆なTTA過程が起こります：

**A-B間でTTAが起こる場合**（$|S_0 T_1 T_1\rangle$ から）:
$$
|S_0 T_1 T_1\rangle \xrightarrow{L_{\text{TTA}}^{AB}} |S_0 S_1 S_0\rangle \text{ または } |S_0 S_0 S_1\rangle
$$

**B-C間でTTAが起こる場合**（$|T_1 T_1 S_0\rangle$ から）:
$$
|T_1 T_1 S_0\rangle \xrightarrow{L_{\text{TTA}}^{BC}} |S_1 S_0 S_0\rangle \text{ または } |S_0 S_1 S_0\rangle
$$

**重要な物理的性質**:

1. **非可逆性**: TTA過程は一方向のみであり、逆反応（S₁ + S₀ → T₁ + T₁）は起こりません
2. **エネルギー保存**: 2E_T1 > E_S1 + E_S0 であり、差分エネルギーが格子振動（熱）として散逸します
3. **混合状態の生成**: リンドブラッド演算子により、純粋状態が混合状態に遷移します
4. **確率的過程**: どちらの生成物（S₁S₀ または S₀S₁）が生成されるかは確率的に決定されます

### 9.3 ポピュレーションダイナミクス

時間発展により、各状態のポピュレーションが変化します：

1. $p_{T_1 S_0 T_1}(t)$ は初期に1で、時間とともに減少
2. $p_{S_0 T_1 T_1}(t)$ と $p_{T_1 T_1 S_0}(t)$ は一時的に増加（A-B間およびB-C間のエネルギー移動）
3. $p_{T_1 T_1 T_1}(t)$ は一時的に増加する可能性（両端から中心へのエネルギー移動）
4. $p_{S_1 S_0 S_0}(t)$、$p_{S_0 S_1 S_0}(t)$、$p_{S_0 S_0 S_1}(t)$ は長時間後に増加（TTA生成物）

### 9.4 線形配列の効果

3分子線形系では、中心分子Bが重要な役割を果たします：

- **エネルギー伝達の媒介**: 両端の分子A、Cからエネルギーを受け取り、TTA過程を促進
- **対称性**: 初期状態 $|T_1 S_0 T_1\rangle$ は左右対称で、A-B間とB-C間で同等の過程が起こる
- **最近接相互作用**: A-C間の直接相互作用がないため、エネルギー移動とTTAは必ず中心分子Bを経由

---

## 10. まとめ

本理論書では、三重項-三重項消滅(TTA)過程の包括的な量子力学的記述を、3分子線形系に拡張して提供しました：

1. **古典的速度論**: 3分子系の速度方程式による記述（TTAは非可逆）
2. **量子力学的記述**: Lindbladマスター方程式による正しい記述
   - 可逆的過程: ハミルトニアン（H_0 + H_ET）
   - 非可逆的過程: リンドブラッド崩壊演算子（L_TTA）
3. **Qubit符号化**: 6量子ビットによる実装
4. **Qudit符号化**: 3 qutritによる直接実装
5. **鈴木-トロッター分解**: Lindbladマスター方程式の時間発展の数値計算法
6. **量子回路**: QiskitとMQTによる実装

### 10.1 3分子系の特徴

- **初期状態**: $|T_1 S_0 T_1\rangle$（両端励起、中心基底）
- **線形配列**: A ⟷ B ⟷ C
- **最近接相互作用**: A-B間とB-C間のみ
- **中心分子の役割**: エネルギー伝達のハブ
- **状態空間**: 27次元（qudit）vs 64次元（qubit）
- **TTA過程**: 非可逆な散逸過程として正しく記述

### 10.2 2分子系からの拡張

2分子系 → 3分子系への主な変更点：

- 状態空間: 9次元 → 27次元
- Qubit数: 4 → 6
- Qutrit数: 2 → 3
- ハミルトニアン項: 2項 → 3項（$H_0 + H_{\text{ET}}^{AB} + H_{\text{ET}}^{BC}$）
- リンドブラッド演算子: 4個（L_TTA^{AB,1}, L_TTA^{AB,2}, L_TTA^{BC,1}, L_TTA^{BC,2}）
- 対称性: 左右対称な初期状態と相互作用

### 10.3 物理的正しさ

**重要**: 本理論では、TTA過程を非可逆な過程として正しく扱っています：

- エネルギー移動（ET）: 可逆的 → ハミルトニアンで記述
- 三重項-三重項消滅（TTA）: 非可逆的 → リンドブラッド演算子で記述

この記述により：
1. エネルギー保存則との整合性が保たれる
2. S₁状態からT₁状態への非物理的な逆反応を排除
3. 系の密度行列が時間発展で適切に混合状態となる
4. ヒューリスティックな近似やfallbackを使用しない厳密な記述

これらの理論は、Jupyter notebookでの数値シミュレーションの基礎となります。

---

## 参考文献

1. Suzuki, M. (1991). "General theory of fractal path integrals with applications to many‐body theories and statistical physics." Journal of Mathematical Physics, 32(2), 400-407.

2. Singh, S., et al. (2015). "Triplet Fusion Upconversion: Progress and Prospects for Solar Energy Applications." Applied Physics Reviews, 2(2), 021302.

3. Lloyd, S. (1996). "Universal Quantum Simulators." Science, 273(5278), 1073-1078.

4. Nielsen, M. A., & Chuang, I. L. (2010). "Quantum Computation and Quantum Information." Cambridge University Press.

5. Schuld, M., & Petruccione, F. (2018). "Supervised Learning with Quantum Computers." Springer.

---

**作成日**: 2025-10-13  
**バージョン**: 1.0
