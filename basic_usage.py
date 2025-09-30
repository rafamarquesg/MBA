from src.detector import ViolenceDetector

detector = ViolenceDetector()
text = "Paciente sofreu trauma contundente e lesão corporal."
result = detector.analyze(text)
print(result)