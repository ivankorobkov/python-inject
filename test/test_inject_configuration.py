import inject
from inject import InjectorException
from test import BaseTestInject


class TestInjectConfiguration(BaseTestInject):
    def test_configure__should_create_injector(self):
        injector0 = inject.configure()
        injector1 = inject.get_injector()
        assert injector0
        assert injector0 is injector1

    def test_configure__should_add_bindings(self):
        injector = inject.configure(lambda binder: binder.bind(int, 123))
        instance = injector.get_instance(int)
        assert instance == 123

    def test_configure__already_configured(self):
        inject.configure()

        self.assertRaisesRegex(InjectorException, 'Injector is already configured', inject.configure)

    def test_configure_once__should_create_injector(self):
        injector = inject.configure_once()
        assert inject.get_injector() is injector

    def test_configure_once__should_return_existing_injector_when_present(self):
        injector0 = inject.configure()
        injector1 = inject.configure_once()
        assert injector0 is injector1

    def test_is_configured__should_return_true_when_injector_present(self):
        assert inject.is_configured() is False

        inject.configure()
        assert inject.is_configured() is True

        inject.clear()
        assert inject.is_configured() is False

    def test_clear_and_configure(self):
        injector0 = inject.configure()
        injector1 = inject.clear_and_configure()  # No exception.
        assert injector0
        assert injector1
        assert injector1 is not injector0

    def test_get_injector_or_die(self):
        self.assertRaisesRegex(InjectorException, 'No injector is configured', inject.get_injector_or_die)

    def test_configure__runtime_binding_disabled(self):
        injector = inject.configure(bind_in_runtime=False)
        self.assertRaisesRegex(InjectorException, "No binding was found for key=<.* 'int'>", injector.get_instance, int)

    def test_configure__install_allow_override(self):
        def base_config(binder):
            binder.bind(int, 123)

        def config(binder):
            binder.install(base_config)
            binder.bind(int, 456)

        injector = inject.configure(config, allow_override=True)
        assert injector.get_instance(int) == 456
