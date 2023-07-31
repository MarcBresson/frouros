"""CVMTest (Cramér-von Mises test) module."""

from typing import Optional, List, Union

import numpy as np  # type: ignore
from scipy.stats import cramervonmises_2samp  # type: ignore

from frouros.callbacks.batch.base import BaseCallbackBatch
from frouros.detectors.data_drift.base import NumericalData, UnivariateData
from frouros.detectors.data_drift.batch.statistical_test.base import (
    BaseStatisticalTest,
    StatisticalResult,
)
from frouros.detectors.data_drift.exceptions import InsufficientSamplesError


class CVMTest(BaseStatisticalTest):
    """CVMTest (Cramér-von Mises test) [cramer1928composition]_ detector.

    :param callbacks: callbacks, defaults to None
    :type callbacks: Optional[Union[BaseCallbackBatch, List[BaseCallbackBatch]]]
    :param kwargs: additional keyword arguments to pass to scipy.stats.cramervonmises_2samp
    :type kwargs: Dict[str, Any]

    :References:

    .. [cramer1928composition] Cramér, Harald.
        "On the composition of elementary errors: First paper: Mathematical deductions."
        Scandinavian Actuarial Journal 1928.1 (1928): 13-74.

    :Example:

    >>> from frouros.detectors.data_drift import CVMTest
    >>> import numpy as np
    >>> np.random.seed(seed=31)
    >>> X = np.random.normal(loc=0, scale=1, size=100)
    >>> Y = np.random.normal(loc=1, scale=1, size=100)
    >>> detector = CVMTest()
    >>> _ = detector.fit(X=X)
    >>> detector.compare(X=Y)[0]
    StatisticalResult(statistic=5.331699999999998, p_value=1.7705426014202885e-10)
    """  # noqa: E501

    def __init__(  # noqa: D107
        self,
        callbacks: Optional[Union[BaseCallbackBatch, List[BaseCallbackBatch]]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            data_type=NumericalData(),
            statistical_type=UnivariateData(),
            callbacks=callbacks,
        )
        self.kwargs = kwargs

    @BaseStatisticalTest.X_ref.setter  # type: ignore[attr-defined]
    def X_ref(self, value: Optional[np.ndarray]) -> None:  # noqa: N802
        """Reference data setter.

        :param value: value to be set
        :type value: Optional[numpy.ndarray]
        """
        if value is not None:
            self._check_sufficient_samples(X=value)
            self._X_ref = value
            # self._X_ref_ = check_array(value)  # noqa: N806
        else:
            self._X_ref = None  # noqa: N806

    def _specific_checks(self, X: np.ndarray) -> None:  # noqa: N803
        self._check_sufficient_samples(X=X)

    @staticmethod
    def _check_sufficient_samples(X: np.ndarray) -> None:  # noqa: N803
        if X.shape[0] < 2:
            raise InsufficientSamplesError("Number of samples must be at least 2.")

    def _statistical_test(
        self, X_ref: np.ndarray, X: np.ndarray, **kwargs  # noqa: N803
    ) -> StatisticalResult:
        test = cramervonmises_2samp(
            x=X_ref,
            y=X,
            method=self.kwargs.get("method", "auto"),
        )
        test = StatisticalResult(statistic=test.statistic, p_value=test.pvalue)
        return test
