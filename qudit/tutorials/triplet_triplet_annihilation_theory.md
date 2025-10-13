# 三重項-三重項消滅(TTA)過程の量子ダイナミクス理論

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

本研究では、二つの色素分子A、Bを含む系において以下の過程を考察します：

1. **励起エネルギー移動**: T₁ → S₀ (エネルギー供与) と S₀ → T₁ (エネルギー受容)
2. **三重項-三重項消滅**: T₁ + T₁ → S₁ + S₀

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

2分子系(A, B)のポピュレーション動力学は以下の速度方程式で記述されます：

$$
\begin{aligned}
\frac{d[A_{S_0}]}{dt} &= -k_{\text{ET}}[A_{S_0}][B_{T_1}] + k_{\text{ET}}[A_{T_1}][B_{S_0}] + k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[A_{T_1}]}{dt} &= k_{\text{ET}}[A_{S_0}][B_{T_1}] - k_{\text{ET}}[A_{T_1}][B_{S_0}] - 2k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[A_{S_1}]}{dt} &= k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[B_{S_0}]}{dt} &= k_{\text{ET}}[A_{T_1}][B_{S_0}] - k_{\text{ET}}[A_{S_0}][B_{T_1}] + k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[B_{T_1}]}{dt} &= k_{\text{ET}}[A_{S_0}][B_{T_1}] - k_{\text{ET}}[A_{T_1}][B_{S_0}] - 2k_{\text{TTA}}[A_{T_1}][B_{T_1}] \\
\frac{d[B_{S_1}]}{dt} &= 0
\end{aligned}
$$

ここで：
- $k_{\text{ET}}$: エネルギー移動速度定数
- $k_{\text{TTA}}$: 三重項-三重項消滅速度定数
- $[X_Y]$: 分子Xの状態Yのポピュレーション

### 3.2 初期条件

$$
\begin{aligned}
[A_{T_1}](0) &= 1, \quad [A_{S_0}](0) = 0, \quad [A_{S_1}](0) = 0 \\
[B_{S_0}](0) &= 1, \quad [B_{T_1}](0) = 0, \quad [B_{S_1}](0) = 0
\end{aligned}
$$

### 3.3 保存則

全ポピュレーションは保存されます：

$$
[A_{S_0}] + [A_{T_1}] + [A_{S_1}] = 1
$$
$$
[B_{S_0}] + [B_{T_1}] + [B_{S_1}] = 1
$$

---

## 4. 量子力学的記述

### 4.1 状態空間

2分子系の全状態空間は、各分子の状態空間のテンソル積です：

$$
\mathcal{H}_{\text{total}} = \mathcal{H}_A \otimes \mathcal{H}_B
$$

各分子の状態空間は3次元：

$$
\mathcal{H}_A = \mathcal{H}_B = \text{span}\{|S_0\rangle, |T_1\rangle, |S_1\rangle\}
$$

全状態空間の次元は $3 \times 3 = 9$ です。

### 4.2 基底状態

2分子系の計算基底は以下の9状態です：

$$
\begin{aligned}
&|S_0 S_0\rangle, |S_0 T_1\rangle, |S_0 S_1\rangle, \\
&|T_1 S_0\rangle, |T_1 T_1\rangle, |T_1 S_1\rangle, \\
&|S_1 S_0\rangle, |S_1 T_1\rangle, |S_1 S_1\rangle
\end{aligned}
$$

### 4.3 ハミルトニアン

系の全ハミルトニアンは以下の4つの項から構成されます（修正版）：

$$
H = H_0 + H_{\text{ET}} + H_{\text{form}} + H_{\text{TTA}}
$$

**重要な修正**: 元の理論では3項のみでしたが、これでは $|T_1 S_0\rangle$ から $|T_1 T_1\rangle$ への経路が存在せず、TTAが起こりません。$H_{\text{form}}$ 項の追加により、この問題が解決されます。

#### 4.3.1 自由ハミルトニアン

各分子の自由ハミルトニアンは対角的です：

$$
H_0 = H_A \otimes I_B + I_A \otimes H_B
$$

ここで：

$$
H_A = H_B = \begin{pmatrix}
E_{S_0} & 0 & 0 \\
0 & E_{T_1} & 0 \\
0 & 0 & E_{S_1}
\end{pmatrix}
$$

通常、基底状態のエネルギーを0に設定します：$E_{S_0} = 0$

$$
H_A = H_B = \begin{pmatrix}
0 & 0 & 0 \\
0 & E_T & 0 \\
0 & 0 & E_S
\end{pmatrix}
$$

ここで、$E_T = E_{T_1}$、$E_S = E_{S_1}$ です。

#### 4.3.2 エネルギー移動ハミルトニアン

エネルギー移動過程は以下の遷移を誘起します：

$$
|T_1 S_0\rangle \leftrightarrow |S_0 T_1\rangle
$$

ハミルトニアンは：

$$
H_{\text{ET}} = V_{\text{ET}} (|T_1 S_0\rangle\langle S_0 T_1| + |S_0 T_1\rangle\langle T_1 S_0|)
$$

ここで、$V_{\text{ET}}$ は結合定数です。

行列表現（基底順序：$|S_0 S_0\rangle, |S_0 T_1\rangle, |S_0 S_1\rangle, |T_1 S_0\rangle, |T_1 T_1\rangle, |T_1 S_1\rangle, |S_1 S_0\rangle, |S_1 T_1\rangle, |S_1 S_1\rangle$）：

$$
H_{\text{ET}} = V_{\text{ET}} \begin{pmatrix}
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0
\end{pmatrix}
$$

#### 4.3.3 T₁T₁形成ハミルトニアン（重要な追加項）

**この項は元の理論に欠けていた重要な項です。**

T₁T₁形成過程は以下の遷移を誘起します：

$$
|T_1 S_0\rangle \leftrightarrow |T_1 T_1\rangle, \quad |S_0 T_1\rangle \leftrightarrow |T_1 T_1\rangle
$$

ハミルトニアンは：

$$
H_{\text{form}} = V_{\text{form}} (|T_1 S_0\rangle\langle T_1 T_1| + |S_0 T_1\rangle\langle T_1 T_1| + \text{h.c.})
$$

ここで、$V_{\text{form}}$ は形成結合定数です。

行列表現：

$$
H_{\text{form}} = V_{\text{form}} \begin{pmatrix}
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & 1 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0
\end{pmatrix}
$$

**物理的解釈**:

この項は、両分子が励起状態にある時の**二体相互作用**を表現します：

1. **双極子-双極子相互作用**: 励起分子間の電気双極子モーメントの相互作用
2. **交換相互作用**: 分子が近接した時の電子波動関数の重なり効果
3. **有効結合**: より高次の仮想状態を経由した実効的な結合

この項がない場合、初期状態 $|T_1 S_0\rangle$ から $|T_1 T_1\rangle$ 状態に到達できず、TTAは決して起こりません。典型的な値は $V_{\text{form}} \sim 0.01\text{-}0.05$ eV です。

#### 4.3.4 三重項-三重項消滅ハミルトニアン

TTA過程は以下の遷移を誘起します：

$$
|T_1 T_1\rangle \rightarrow |S_1 S_0\rangle + |S_0 S_1\rangle
$$

ハミルトニアンは：

$$
H_{\text{TTA}} = V_{\text{TTA}} (|S_1 S_0\rangle\langle T_1 T_1| + |S_0 S_1\rangle\langle T_1 T_1| + \text{h.c.})
$$

行列表現：

$$
H_{\text{TTA}} = V_{\text{TTA}} \begin{pmatrix}
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0
\end{pmatrix}
$$

### 4.4 時間発展

シュレーディンガー方程式：

$$
i\hbar \frac{d|\psi(t)\rangle}{dt} = H |\psi(t)\rangle
$$

形式解：

$$
|\psi(t)\rangle = e^{-iHt/\hbar} |\psi(0)\rangle = U(t) |\psi(0)\rangle
$$

ここで、$U(t) = e^{-iHt/\hbar}$ は時間発展演算子です。

### 4.5 初期状態

初期状態は：

$$
|\psi(0)\rangle = |T_1 S_0\rangle
$$

### 4.6 観測量

各状態のポピュレーションは射影演算子で測定されます：

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

### 5.2 2分子系の符号化

2分子系は4量子ビットで表現されます（各分子に2量子ビット）：

$$
|X_A X_B\rangle \rightarrow |\text{code}(X_A)\rangle \otimes |\text{code}(X_B)\rangle
$$

例：
$$
\begin{aligned}
|T_1 S_0\rangle &\rightarrow |01\rangle \otimes |00\rangle = |0100\rangle \\
|S_0 T_1\rangle &\rightarrow |00\rangle \otimes |01\rangle = |0001\rangle \\
|T_1 T_1\rangle &\rightarrow |01\rangle \otimes |01\rangle = |0101\rangle \\
|S_1 S_0\rangle &\rightarrow |10\rangle \otimes |00\rangle = |1000\rangle \\
|S_0 S_1\rangle &\rightarrow |00\rangle \otimes |10\rangle = |0010\rangle
\end{aligned}
$$

### 5.3 パウリ演算子による演算子の構成

#### 5.3.1 基本演算子

単一量子ビットのパウリ演算子：

$$
\begin{aligned}
\sigma_x &= \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad
\sigma_y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad
\sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} \\
I &= \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}
\end{aligned}
$$

#### 5.3.2 射影演算子

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

### 6.3 2分子系の表現

2分子系は2つのqutritで表現されます：

$$
|X_A X_B\rangle \rightarrow |i\rangle_3 \otimes |j\rangle_3
$$

全状態空間の次元は $3 \times 3 = 9$ です。

### 6.4 演算子の表現

#### 6.4.1 Gell-Mann行列

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

#### 6.4.2 昇降演算子

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
H = H_1 + H_2 + \cdots + H_n
$$

時間発展演算子は：

$$
U(t) = e^{-iHt} = e^{-i(H_1 + H_2 + \cdots + H_n)t}
$$

一般に、$[H_i, H_j] \neq 0$ のため、この指数関数を単純に分解できません。

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

### 7.5 本問題への適用

我々の系では：

$$
H = H_0 + H_{\text{ET}} + H_{\text{TTA}}
$$

各項は可換でないため、トロッター分解を適用します：

$$
U(\Delta t) \approx e^{-iH_0\Delta t/2} e^{-iH_{\text{ET}}\Delta t/2} e^{-iH_{\text{TTA}}\Delta t} e^{-iH_{\text{ET}}\Delta t/2} e^{-iH_0\Delta t/2}
$$

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

1. **初期化**: $|0100\rangle$ 状態の準備
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

- **量子ビット数**: 4
- **ゲート数**: トロッターステップ数とハミルトニアン項の複雑さに依存
- **回路深さ**: トロッターステップ数に比例

#### 8.1.4 シミュレーション

- **Statevectorシミュレータ**: 正確な量子状態ベクトルを計算
- **ショットシミュレータ**: 測定の統計的サンプリング（例：10000ショット）

### 8.2 Qudit実装（MQT）

#### 8.2.1 回路構成

1. **初期化**: $|10\rangle_3$ 状態の準備（分子A: $|1\rangle_3$、分子B: $|0\rangle_3$）
2. **トロッター分解**: 各ハミルトニアン項をquditゲートに分解
3. **測定**: 全quditを計算基底で測定

#### 8.2.2 Quditゲート

- **単一quditゲート**: $U \in SU(3)$
- **2-quditゲート**: $U \in SU(9)$

MQT（Munich Quantum Toolkit）は、任意の次元のquditをサポートします。

#### 8.2.3 回路メトリクス

- **Qudit数**: 2（各分子に1 qutrit）
- **ゲート数**: Qubit実装より少ない（直接3準位演算）
- **回路深さ**: Qubit実装より浅い可能性

#### 8.2.4 シミュレーション

- **Statevectorシミュレータ**: 9次元の状態ベクトルを計算
- **ショットシミュレータ**: 測定の統計的サンプリング

### 8.3 比較分析

| 項目 | Qubit (Qiskit) | Qudit (MQT) |
|------|----------------|-------------|
| 量子資源数 | 4 qubits | 2 qutrits |
| 状態空間次元 | 16 (未使用: 7) | 9 |
| ゲート数 | 多い | 少ない |
| 回路深さ | 深い | 浅い |
| 実装の複雑さ | 標準的 | 新しい技術 |
| ハードウェア対応 | 広く利用可能 | 限定的 |

---

## 9. 物理的解釈

### 9.1 エネルギー移動

初期状態 $|T_1 S_0\rangle$ から始まり、エネルギー移動により $|S_0 T_1\rangle$ への遷移が起こります：

$$
|T_1 S_0\rangle \xrightarrow{H_{\text{ET}}} \alpha|T_1 S_0\rangle + \beta|S_0 T_1\rangle
$$

### 9.2 三重項-三重項消滅

両方の分子が三重項状態 $|T_1 T_1\rangle$ にある場合、TTA過程により一方が一重項励起状態に遷移します：

$$
|T_1 T_1\rangle \xrightarrow{H_{\text{TTA}}} \gamma|S_1 S_0\rangle + \delta|S_0 S_1\rangle
$$

### 9.3 ポピュレーションダイナミクス

時間発展により、各状態のポピュレーションが変化します：

1. $p_{T_1 S_0}(t)$ は減少
2. $p_{S_0 T_1}(t)$ は増加後、減少
3. $p_{T_1 T_1}(t)$ は一時的に増加
4. $p_{S_1 S_0}(t)$ と $p_{S_0 S_1}(t)$ は長時間後に増加

---

## 10. まとめ

本理論書では、三重項-三重項消滅(TTA)過程の包括的な量子力学的記述を提供しました：

1. **古典的速度論**: 速度方程式による記述
2. **量子力学的記述**: ハミルトニアンと時間発展
3. **Qubit符号化**: 4量子ビットによる実装
4. **Qudit符号化**: 2 qutritによる直接実装
5. **鈴木-トロッター分解**: 時間発展の数値計算法
6. **量子回路**: QiskitとMQTによる実装

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
