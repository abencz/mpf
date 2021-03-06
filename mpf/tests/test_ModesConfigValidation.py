from mpf.tests.MpfTestCase import MpfTestCase


class TestModesConfigValidation(MpfTestCase):

    def getConfigFile(self):
        return self.config

    def getMachinePath(self):
        return 'tests/machine_files/mode_tests/'

    def setUp(self):

        self.add_to_config_validator('unrelated_section',
                                     dict(__valid_in__ = 'mode'))

        self.save_and_prepare_sys_path()

    def tearDown(self):
        self.restore_sys_path()

    def test_loading_invalid_modes(self):
        self.config = 'test_loading_invalid_modes.yaml'
        with self.assertRaises(ValueError) as context:
            super(TestModesConfigValidation, self).setUp()

        self.assertEqual("No folder found for mode 'invalid'. Is your "
                         "mode folder in your machine's 'modes' folder?",
                         str(context.exception))

    def test_broken_mode_config(self):
        self.config = 'test_broken_mode_config.yaml'
        with self.assertRaises(AssertionError) as context:
            super(TestModesConfigValidation, self).setUp()

        self.assertEqual('Your config contains a value for the setting "'
                         'mode:invalid_key", but this is not a valid '
                         'setting name.', str(context.exception))

    def test_missing_mode_section(self):
        self.config = 'test_missing_mode_section.yaml'
        super(TestModesConfigValidation, self).setUp()

        self.assertTrue("broken_mode2" in self.machine.modes)
