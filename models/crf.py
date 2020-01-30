from sklearn_crfsuite import CRF

from .tools import sent2features, sent2features_tagged


class CRFModel(object):
    def __init__(self,
                 algorithm='lbfgs',
                 c1=0.1,
                 c2=0.1,
                 max_iterations=100,
                 all_possible_transitions=False
                 ):

        self.model = CRF(algorithm=algorithm,
                         c1=c1,
                         c2=c2,
                         max_iterations=max_iterations,
                         all_possible_transitions=all_possible_transitions)

    def train(self, sentences, tag_lists, tagged=False):
        if tagged:
            features = [sent2features_tagged(s) for s in sentences] 
        else:
            features = [sent2features(s) for s in sentences]
        self.model.fit(features, tag_lists)

    def test(self, sentences, tagged=False):
        if tagged:
            features = [sent2features_tagged(s) for s in sentences]
            pred_tag_lists = self.model.predict(features)
        else:
            features = [sent2features(s) for s in sentences]
            pred_tag_lists = self.model.predict(features)
        return pred_tag_lists
