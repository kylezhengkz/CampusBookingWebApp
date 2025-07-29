import os
from typing import Optional, Tuple, List, Dict, Any

import PyUtils as PU
import Backend as BK

from .BaseUnitTest import BaseUnitTest


class AF2Test(BaseUnitTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testFolder = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF2", "tests")
        cls.dashboardService = BK.DashboardService(cls.dbTool)

    def parseArgs(self, testName: str, testFolder: Optional[str] = None) -> Tuple[List[Any], Dict[str, Any]]:
        args, kwargs = self.loadArgs(testName, testFolder = testFolder)
        return (args, kwargs)

    def runTest(self, testName: str):
        args, kwargs = self.parseArgs(testName)

        success, result = self.dashboardService.getDashboardMetrics(*args, **kwargs)
        self.evalOutFile(f"{result}", testName)

    # ======================================================

    def test_userIdNotValid_error(self):
        self.runTest("InvalidUser")

    def test_userNotExsits_noBookingMetrics(self):
        self.runTest("UserNotExists")

    def test_noBookings_noBookingMetrics(self):
        self.runTest("NoBookings")

    def test_hasBookings_hasBookingMetrics(self):
        self.runTest("HasBookings")