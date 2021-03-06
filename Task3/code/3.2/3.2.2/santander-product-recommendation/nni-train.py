import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from collections import defaultdict
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from nni.feature_engineering.gradient_selector import FeatureGradientSelector

usecols = [
    'ncodpers', 'ind_ahor_fin_ult1', 'ind_aval_fin_ult1', 'ind_cco_fin_ult1',
    'ind_cder_fin_ult1', 'ind_cno_fin_ult1', 'ind_ctju_fin_ult1',
    'ind_ctma_fin_ult1', 'ind_ctop_fin_ult1', 'ind_ctpp_fin_ult1',
    'ind_deco_fin_ult1', 'ind_deme_fin_ult1', 'ind_dela_fin_ult1',
    'ind_ecue_fin_ult1', 'ind_fond_fin_ult1', 'ind_hip_fin_ult1',
    'ind_plan_fin_ult1', 'ind_pres_fin_ult1', 'ind_reca_fin_ult1',
    'ind_tjcr_fin_ult1', 'ind_valo_fin_ult1', 'ind_viv_fin_ult1',
    'ind_nomina_ult1', 'ind_nom_pens_ult1', 'ind_recibo_ult1'
]

train = pd.read_csv('dataset/train_ver2.csv', usecols=usecols)
sample = pd.read_csv('dataset/sample_submission.csv')
train = train.drop_duplicates(['ncodpers'], keep='last')
train.fillna(0, inplace=True)
model_pred = {}
ids = train.ncodpers.values
pred = defaultdict(list)

for col in train.columns:
    if col != 'ncodpers':
        y_train = train[col]
        x_train = train.drop(['ncodpers', col], axis=1)

        y_train_as_matrix = y_train.values
        y_train_as_matrix = np.matrix(y_train_as_matrix.reshape(
            (-1, 1))).astype(float)
        fgs = FeatureGradientSelector(classification=False,
                                      n_epochs=20,
                                      verbose=1,
                                      batch_size=10000000,
                                      n_features=15)
        fgs.fit(x_train, y_train_as_matrix)
        print(fgs.get_selected_features())

        selected_feature_indices = fgs.get_selected_features()
        x_train = x_train.iloc[:, selected_feature_indices]

        clf = LogisticRegression(max_iter=5000)
        clf.fit(x_train, y_train)
        y_pred = clf.predict_proba(x_train)[:, 1]
        model_pred[col] = y_pred

        for id, y_hat in zip(ids, y_pred):
            pred[id].append(y_hat)

        print('ROC Socre : %f' % (roc_auc_score(y_train, y_pred)))

active_ = {}
for val in train.values:
    val = list(val)
    id = val.pop(0)  ## pop ncodpers (customer id)
    ## active column
    active = [c[0] for c in zip(train.columns[1:], val) if c[1] > 0]
    active_[id] = active

train_preds = {}
for id, val in pred.items():
    preds = [
        i[0] for i in sorted([
            i for i in zip(train.columns[1:], val) if i[0] not in active_[id]
        ],
                             key=lambda i: i[1],
                             reverse=True)[:7]
    ]
    train_preds[id] = preds

test_preds = []
for row in sample.values:
    id = row[0]
    p = train_preds[id]
    test_preds.append(' '.join(p))

sample['added_products'] = test_preds
sample.to_csv('recommendation.csv', index=False)
