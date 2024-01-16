import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.0

ApplicationWindow {

	property string curImagePath: ""
	property bool curImgMirror: false

	property string timerValue: "00:00"
	property string timerColor: "white"

	property QtObject backend

	property int window_width : 512
	property int window_height : 860

	visible: true
	width: window_width
	height: window_height
	title: "Just Draw!"
	//flags: Qt.FramelessWindowHint | Qt.Window

	Connections {
		target: backend

		function onSetcurtimer(val, col) {
			timerValue = val;
			timerColor = col;
		}

		function onSetcurimage(msg) {
			curImagePath = msg;
			curImgMirror = false;
		}

		function onSetcurimagemirror(msg) {
			curImagePath = msg;
			curImgMirror = !curImgMirror;
		}

		function onSetwindowsize(w, h) {
			window_width = w;
			window_height = h;
		}
	}

	Rectangle {
		anchors {
			fill: parent
		}

		color: "#000000"

		Image {
			id: img
			anchors.fill: parent
			source: curImagePath
			width: 512
			height: 860
			autoTransform: true
			mipmap: true
			smooth: true
			mirror: curImgMirror
			fillMode: Image.PreserveAspectFit
			//fillMode: Image.PreserveAspectCrop
		}

		Frame {
			id: timer
			anchors {
				top: parent.top
				right: parent.right
				margins: 12
			}

			background: Rectangle {
				opacity: 0.5
				color: "#101010"
				radius: 10
			}

			Text {
				anchors {
					fill: parent
				}

				text: timerValue
				font.pixelSize: 24
				color: timerColor
			}
		}

		Frame {
			id: panel

			anchors {
				horizontalCenter: parent.horizontalCenter
				bottom: parent.bottom
				margins: 48
			}

			opacity: hovered ? 0.7 : 0.3

			background: Rectangle {
				color: "#101010"
				radius: 10
			}

			RowLayout {
				anchors.fill: parent

				Button {
					id: prevButton

					background: Image {
						source: "./images/prev.png"
					}

					onClicked: {
						backend.prev();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: prevInFolderButton

					background: Image {
						source: "./images/prev_in_folder.png"
					}

					onClicked: {
						backend.prev_in_folder();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: pauseButton

					background: Image {
						source: "./images/pause.png"
					}

					onClicked: {
						backend.pause();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: copyButton

					background: Image {
						source: "./images/copy.png"
					}

					onClicked: {
						backend.copy();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: infoButton

					background: Image {
						source: "./images/info.png"
					}

					onClicked: {
						popup.open();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: excludeButton

					background: Image {
						source: "./images/exclude_folder.png"
					}

					onClicked: {
						backend.exclude_folder();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: mirrorButton

					background: Image {
						source: "./images/mirror.png"
					}

					onClicked: {
						backend.mirror();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: nextInFolderButton

					background: Image {
						source: "./images/next_in_folder.png"
					}

					onClicked: {
						backend.next_in_folder();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}

				Button {
					id: nextButton

					background: Image {
						source: "./images/next.png"
					}

					onClicked: {
						backend.next();
					}

					opacity: pressed ? 1 : hovered ? 0.8 : 0.2
				}
			}
		}

		Popup {
			id: popup

			height: 36
			width: parent.width - height

			x: height/2
			y: parent.height - height

			modal: false
			focus: false

			closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

			background: Rectangle {
				opacity: 0.5
				color: "#101010"
				radius: 10
			}

			Text {
				anchors {
					fill: parent
				}

				text: curImagePath
				font.pixelSize: 14
				color: "white"
			}
		}
	}
}
