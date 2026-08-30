# AI Lead Conversion Platform

[English](README.md) | **日本語**

2024年にドイツ・ウルムのAIハッカソンで開発したリードコンバージョン予測プロトタイプを、プライバシーに配慮して再構築するプロジェクトです。

再現可能な機械学習パイプライン、予測API、Webダッシュボード、LLM支援によるアウトリーチ文面生成を統合する計画です。公開実装では合成CRMデータのみを使用します。

> [!IMPORTANT]
> 2024年のオリジナルプロトタイプはチームプロジェクトであり、ハッカソンで受賞しました。本リポジトリは2026年に独立して再構築したもので、元の企業データセット、社内文書、認証情報、プロプライエタリなソースファイルは含みません。再構築版そのものが受賞成果物という意味ではありません。

## プロジェクトの目的

営業チームが保有するリード数は、手作業で確認できる量を上回る場合があります。本プロジェクトでは、個人情報や企業データを公開せずに、リードの優先順位付け、予測根拠の確認、人がレビューできるアウトリーチ文面の下書き生成を実現する方法を検証します。

## 想定ユーザーフロー

1. 個人を特定できない、元データに近い形式のリード／リードノートを生成
2. 過去の`ObjectID` → `ParentObjectID`関係を再構築
3. データリーケージ対策を含めて過去の結合・縮約フローを再現
4. Baseline、Random Forest、XGBoost分類器を比較
5. FastAPIエンドポイントからコンバージョン予測を要求
6. React／TypeScriptダッシュボードでモデル根拠を確認
7. 任意のLLM Adapterで編集可能なアウトリーチ下書きを生成

## 再構築の方針

- 元レコードを公開せず、2024年の公開ノートブックから確認できるスキーマと集計分布に基づいて公開データを設計
- 現在の特徴量だけに合わせず、幅広い生CRMデータと縮約後のモデリングデータを区別
- リード単位でデータを分割し、結果発生後の情報を除外してEntity Leakage／Target Leakageを防止
- 学習データでFitした前処理と評価データを分離
- AccuracyだけでなくMacro-F1、Recall、Precision、ROC-AUC、混同行列を報告
- 生成文面を自動意思決定ではなく、人が確認する下書きとして扱う
- テスト、Docker、GitHub Actionsにより再現性を確保

## 現在の状況

**Phase 1 — 集計値で較正した合成データ基盤**

- [x] 公開／非公開データ境界を文書化
- [x] 最小構成のヘルスチェックAPIとテストを追加
- [x] 過去のリード／ノートの生データ形状と結合関係を再構築
- [x] 公開可能なCRM集計プロファイルを文書化
- [x] 観測可能な集計特性に合わせたプライバシー安全な合成データGenerator
- [ ] 過去の結合・縮約処理とリーケージ安全な前処理
- [ ] 再現可能なEDAサマリーと診断チャート
- [ ] モデルBaselineと実験レポート
- [ ] 予測・説明API
- [ ] React／TypeScriptダッシュボード
- [ ] 任意のLLM Message Adapter
- [ ] Docker ComposeとCI Workflow

計画の詳細は[ロードマップ](docs/ROADMAP.md)を参照してください。

## クイックスタート

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn lead_intelligence.api:app --reload
```

`http://127.0.0.1:8000/health`を開きます。

テスト：

```bash
pytest
```

## 合成CRMデータ

公開されている元ノートブックでは、幅広い`leads.csv`（86,244行 × 181列）と、1対多の`lead_notes.csv`（134,793行 × 16列）を使用していました。両者を`ObjectID = ParentObjectID`で結合し、より小さな作業用データセットへ縮約しています。

本再構築版でもこの分離を維持し、公開されている集計出力から次の特性を較正しています。

- 確認可能な5種類のWorkflow Status比率
- 39種類すべての`Source_Text`出現頻度
- Noteを持つLeadの比率と平均Note数
- 過去の作業対象におけるField別欠損率
- Owner、Sales Unit、Territory、Lead NameのCardinality／偏り
- 複数の日付形式、言語比率、ノイズを含むNote Placeholder

公開レコードはすべて新しく生成したものです。過去のID、顧客・従業員名、自由記述Noteをコピー、マスキング、翻訳、サンプリングしていません。

したがって本データは、元データを匿名化したものではなく、**集計値で較正した合成データ**です。完全な公開分布を確認できない特性は、過去の事実として推測せず、明示的な近似値として扱います。

小規模サンプル：

- `data/synthetic/leads_sample.csv`
- `data/synthetic/lead_notes_sample.csv`

根拠、較正範囲、残る近似については[Synthetic CRM仕様](docs/DATA_PIPELINE.md)と[Historical CRM集計プロファイル](docs/HISTORICAL_DATA_PROFILE.md)を参照してください。

## リポジトリ境界

- `src/lead_intelligence/`：PythonアプリケーションとMLコード
- `tests/`：自動テスト
- `frontend/`：今後実装するReact／TypeScript Client
- `data/synthetic/`：新規生成した非識別サンプルのみ
- `docs/`：プロジェクト履歴、データポリシー、技術判断

過去成果物との境界とAttribution Policyは[Original project context](docs/ORIGINAL_PROJECT.md)、取扱ルールは[Data and secrets policy](docs/DATA_POLICY.md)を参照してください。

## ライセンス

現時点ではライセンスを選定していません。外部での再利用・配布前に、著作権、ライセンス、Attributionの境界を確認します。
