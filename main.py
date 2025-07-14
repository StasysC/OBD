from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import obd

class EngineHoursApp(App):
    def build(self):
        self.connection = None
        self.label = Label(text="Press to connect to OBD")
        button = Button(text="Get Engine Hours")
        button.bind(on_press=self.get_engine_hours)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(button)

        return layout

    def connect_obd(self):
        if not self.connection:
            self.connection = obd.OBD()  # Auto-connect to Bluetooth OBD-II adapter

    def get_engine_hours(self, instance):
        self.connect_obd()
        cmd = obd.commands.RUN_TIME
        response = self.connection.query(cmd)
        if not response.is_null():
            self.label.text = f"Engine Hours: {response.value}"
        else:
            self.label.text = "Failed to read Engine Hours"

if __name__ == '__main__':
    EngineHoursApp().run()
