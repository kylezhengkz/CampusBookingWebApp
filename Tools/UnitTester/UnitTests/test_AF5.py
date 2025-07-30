import os
import pytz
import uuid

from typing import Optional, Tuple, List, Dict, Any

import PyUtils as PU
import Backend as BK

from .BaseUnitTest import BaseUnitTest


class AF5Test(BaseUnitTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testFolder = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF5", "tests")
        cls.usernameTestFolder = os.path.join(cls.testFolder, "AF5a")
        cls.passwordTestFolder = os.path.join(cls.testFolder, "AF5b")

        cls.userService = BK.UserService(cls.dbTool)

    def setUp(self):
        self.userId: Optional[uuid.UUID] = None
        self.oldUsername: Optional[str] = None
        self.oldPassword: Optional[str] = None

    def tearDown(self):
        if (self.userId is None):
            return
        
        if (self.oldUsername is not None):
            self.revertUsernameChange()

        if (self.oldPassword is not None):
            self.revertPasswordChange()
    
    def revertUsernameChange(self):
        sql = 'UPDATE "User" SET "username" = %(oldUsername)s WHERE "userID" = %(userID)s;'
        self.dbTool.executeSQL(sql, vars = {"oldUsername": self.oldUsername, "userID": str(self.userId)}, commit = True)

    def revertPasswordChange(self):
        sql = 'UPDATE "User" SET "password" = %(oldPassword)s WHERE "userID" = %(userID)s;'
        self.dbTool.executeSQL(sql, vars = {"oldPassword": self.oldPassword, "userID": str(self.userId)}, commit = True)

    def getUsername(self, userId: uuid.UUID) -> Optional[str]:
        sql = 'SELECT "username" FROM "User" WHERE "userID" = %(userID)s;'
        connData, cursor, error = self.dbTool.executeSQL(sql, vars = {"userID": str(userId)})

        if (cursor.rowcount == 0):
            return None
        return cursor.fetchone()[0]
    
    def getPassword(self, userId: uuid.UUID) -> Optional[str]:
        sql = 'SELECT "password" FROM "User" WHERE "userID" = %(userID)s;'
        connData, cursor, error = self.dbTool.executeSQL(sql, vars = {"userID": str(userId)})

        if (cursor.rowcount == 0):
            return None
        return cursor.fetchone()[0]

    def runUsernameTest(self, testName: str):
        args, kwargs = self.loadArgs(testName, testFolder = self.usernameTestFolder)
        args[0] = uuid.UUID(args[0])

        self.userId = args[0]
        self.oldUsername = self.getUsername(self.userId)

        success, msg = self.userService.updateUsername(*args, **kwargs)
        self.evalOutFile(msg, testName, testFolder = self.usernameTestFolder)

    def runPasswordTest(self, testName: str):
        args, kwargs = self.loadArgs(testName, testFolder = self.passwordTestFolder)
        args[0] = uuid.UUID(args[0])

        self.userId = args[0]
        self.oldPassword = self.getPassword(self.userId)

        success, msg = self.userService.updatePassword(*args, **kwargs)
        self.evalOutFile(msg, testName, testFolder = self.passwordTestFolder)

    # ======================================================
    # ================== updateUsername ====================

    def test_userNotExists_usernameNotUpdated(self):
        self.runUsernameTest("UserNotExists")

    def test_usernameTaken_usernameNotUpdated(self):
        self.runUsernameTest("UsernameTaken")

    def test_uniqueUsername_usernameUpdated(self):
        self.runUsernameTest("UsernameChanged")

    # ======================================================
    # ================== updatePassword ====================

    def test_userNotExists_passwordNotUpdated(self):
        self.runPasswordTest("UserNotExists")

    def test_incorrectOldPassword_passwordNotUpdated(self):
        self.runPasswordTest("IncorrectOldPassword")

    def test_correctOldPassword_passwordUpdated(self):
        self.runPasswordTest("PasswordChanged")

    # ======================================================

    