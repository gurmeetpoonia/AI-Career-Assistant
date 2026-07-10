import { useState, useEffect, useRef } from "react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

function App(props) {
  const [text, setText] = useState("");
  const [interimText, setInterimText] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    const defaultText = props.args.default_text || "";

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    setListening(false);
    setInterimText("");
    setText(defaultText);

  }, [props.args.default_text]);

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [text, interimText]);

  // Speech recognition setup
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let finalTranscript = "";
      let interim = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + " ";
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      if (finalTranscript) {
        setText((prev) => (prev + " " + finalTranscript).trim());
      }
      setInterimText(interim);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current = recognition;
  }, []);

  // Tab switch detection
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        Streamlit.setComponentValue({ type: "tab_switch", value: text });
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [text]);

  const startListening = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setListening(true);

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;

      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const animate = () => {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        setAudioLevel(sum / dataArray.length);
        animationRef.current = requestAnimationFrame(animate);
      };

      animate();
    }
  };

  const stopListening = () => {
    recognitionRef.current.stop();
    cancelAnimationFrame(animationRef.current);
    setListening(false);
    setAudioLevel(0);
    setInterimText("");

    Streamlit.setComponentValue({
      type: "text",
      value: text,
    });
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleBlur = () => {
    Streamlit.setComponentValue({ type: "text", value: text });
  };

  return (
      <div style={{ position: "relative", width: "100%" }}>
        <style>{`
          /* पल्स एनिमेशन को अब रेड से बदलकर आपके थीम के ग्रीन कलर (#10a37f) में कर दिया है */
          @keyframes pulseRing {
            0% { box-shadow: 0 0 0 0 rgba(16, 163, 127, 0.6); }
            70% { box-shadow: 0 0 0 14px rgba(16, 163, 127, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 163, 127, 0); }
          }
          .mic-btn-listening {
            animation: pulseRing 1.2s infinite;
          }
        `}</style>
        
        <textarea
          value={text + (interimText ? " " + interimText : "")}
          onChange={handleTextChange}
          onBlur={handleBlur}
          placeholder="Type your answer or use the mic..."
          style={{
            width: "100%",
            minHeight: "170px",
            background: "#212121",
            color: "#ECECEC",
            /* 2. माइक ON होने पर रेड बॉर्डर की जगह ग्रीन थीम (#10a37f) बॉर्डर दिया है */
            border: listening ? "1px solid #10a37f" : "1px solid #3a3a3a",
            borderRadius: "14px",
            padding: "16px 55px 16px 16px",
            fontSize: "16px",
            lineHeight: "1.6",
            resize: "vertical",
            boxSizing: "border-box",
            outline: "none",
            transition: "all 0.2s ease",
          }}
        />

        {/* वेव एनिमेशन */}
        {listening && (
          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              gap: "4px",
              height: "45px",
              marginTop: "12px",
            }}
          >
            {[...Array(18)].map((_, i) => (
              <div
                key={i}
                style={{
                  width: "4px",
                  borderRadius: "10px",
                  background: "#10a37f",
                  height: `${8 + Math.random() * audioLevel}px`,
                  transition: "0.08s",
                }}
              />
            ))}
          </div>
        )}

        {/* माइक बटन */}
        <button
          onClick={listening ? stopListening : startListening}
          className={listening ? "mic-btn-listening" : ""}
          style={{
            position: "absolute",
            /* वेव एनिमेशन नीचे आने की वजह से बटन की पोजीशन थोड़ी एडजस्ट की है ताकि टेक्स्टएरिया के अंदर परफेक्ट दिखे */
            bottom: listening ? "68px" : "12px",
            right: "12px",
            width: "42px",
            height: "42px",
            borderRadius: "50%",
            border: "none",
            /* 3. माइक ON होने पर रेड स्क्वायर (⏹) के पीछे का बैकग्राउंड लाल के बजाय डार्क ही रखा है ताकि भड़कीला न लगे */
            background: listening ? "#2f2f2f" : "#2f2f2f",
            /* 4. ऑन होने पर आइकॉन का रंग लाल के बजाय हरा (#10a37f) कर दिया है, और वह गोल बटन के अंदर ही रहेगा */
            color: listening ? "#10a37f" : "white",
            cursor: "pointer",
            fontSize: "16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: listening ? "scale(1.08)" : "scale(1)",
            transition: "all .2s ease",
          }}
        >
          {listening ? "⏹" : "🎙️"}
        </button>
      </div>
  );
}

export default withStreamlitConnection(App);