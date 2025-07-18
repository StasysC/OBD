from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform
import obd
import logging
import os

# Only request permissions on Android
if platform == 'android':
    from android.permissions import request_permissions, Permission

# It's good practice to get the logger instance at the module level
logger = logging.getLogger(__name__)


def setup_logging():
    """
    Configures logging to file and console.
    On Android, it will log to the app's specific external storage directory.
    """
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    log_path = ''
    if platform == 'android':
        # Get the app's specific directory on external storage
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        app_folder = context.getExternalFilesDir(None).getAbsolutePath()
        log_path = os.path.join(app_folder, 'logs.log')
    else:
        # For other platforms (like desktop), log in the current directory
        log_path = './logs.log'

    # Ensure the directory for the log file exists
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # File handler for logging to a file
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for logging to the console (useful for debugging)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging configured. Log path: %s", log_path)
    return logger


class EngineHoursApp(App):
    def build(self):
        """
        Builds the user interface for the application.
        """
        self.connection = None
        self.label = Label(text="Not connected to OBD")
        button = Button(text="Get Engine Hours")
        button.bind(on_press=self.get_engine_hours)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(button)

        return layout

    def on_start(self):
        """
        This method is called when the app starts.
        It's a good place to request necessary permissions.
        """
        if platform == 'android':
            self.request_android_permissions()

    def request_android_permissions(self):
        """
        Requests necessary permissions on Android.
        """
        def callback(permissions, results):
            if all([res for res in results]):
                logger.info("All permissions granted.")
                # You can now proceed with operations that require these permissions
            else:
                logger.warning("Not all permissions were granted.")
                self.label.text = "Storage permission denied. Logging to file might fail."

        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], callback)

    def connect_obd(self):
        """
        Establishes a connection to the OBD-II adapter.
        """
        if not self.connection:
            try:
                self.connection = obd.OBD()  # Auto-connect to Bluetooth OBD-II adapter
                if self.connection.is_connected():
                    self.label.text = "Connected to OBD"
                    logger.info("Successfully connected to OBD.")
                else:
                    self.label.text = "Failed to connect to OBD"
                    logger.warning("obd.OBD() did not establish a connection.")
            except Exception as e:
                self.label.text = "Error connecting to OBD"
                logger.error("Exception during OBD connection: %s", e, exc_info=True)
        else:
             self.label.text = "Already connected to OBD"


    def get_engine_hours(self, instance):
        """
        Fetches the engine run time from the OBD-II adapter.
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect_obd()

            if self.connection and self.connection.is_connected():
                cmd = obd.commands.RUN_TIME
                response = self.connection.query(cmd)
                if response and not response.is_null():
                    self.label.text = f"Engine Hours: {response.value}"
                    logger.info("Successfully retrieved engine hours: %s", response.value)
                else:
                    self.label.text = "Failed to read Engine Hours"
                    logger.warning("Failed to read Engine Hours, response was null.")
        except Exception as e:
            self.label.text = "Error getting engine hours"
            logger.error("Exception while getting engine hours: %s", e, exc_info=True)


def main():
    # Setup logging before running the app
    setup_logging()
    logger.info("App starting...")
    EngineHoursApp().run()


if __name__ == '__main__':
    main()