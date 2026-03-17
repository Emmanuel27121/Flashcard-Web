import {useState} from "react";
import "./App.css";
import UploadPanel from "./components/UploadPanel.jsx";
import StudyPanel from "./components/StudyPanel.jsx";
import { uploadPdf,getCards,getStatus,downloadCsvUrl } from "./api/client.js";

export default function App() {
	const [selectedFile, setSelectedFile] = useState(null);
	const [status, setStatus] = useState("idle");
	const [statusMessage, setStatusMessage] = useState("");
	const [cards, setCards] = useState([]);
	const [currentIndex, setCurrentIndex] = useState(0);
	const [showAnswer, setShowAnswer] = useState(false);
	const [chunkSize, setChunkSize] = useState(2);
	const currentCard = cards[currentIndex];
	const [lastGeneratedJobId, setLastJobId] = useState(null);
	
	function handleChooseFile(file) {
		setSelectedFile(file);
		setCards([]);
		setCurrentIndex(0);
		setShowAnswer(false);
		setStatus("idle");
		setStatusMessage("");
	}

	async function handleGenerate() {
		if(!selectedFile) return;
		
		try{
			setStatus("working");
			setStatusMessage("Generating flashcards");

			const { job_id } = await uploadPdf(selectedFile, 1);

			while(true){
				const statusRes = await getStatus(job_id);
				setStatusMessage(statusRes.message || "Working...");

				if(statusRes.status === "done"){break;}
				if(statusRes.status === "error"){
					throw new Error(statusRes.message || "An error occurred during processing.");
				}
				
				await new Promise((r) => setTimeout(r, 1000));
			}

			setStatus("Fetching flashcards...");
			const fetchedCards = await getCards(job_id);
			setCards(fetchedCards);
			setStatus("done");
			setStatusMessage(`Done — ${fetchedCards.length} cards ready`);

			setLastJobId(job_id);
			
		}catch(err){
			setStatus("error");
			setStatusMessage(err.message);
		}

		

	}

	function handlePrev() {
		setShowAnswer(false);
		setCurrentIndex((i) => Math.max(0, i - 1));
	}

	function handleNext() {
		setShowAnswer(false);
		setCurrentIndex((i) => Math.min(cards.length - 1, i + 1));
	}

	function handleFlip() {
		setShowAnswer((v) => !v);
	}

	function handleDownload() {
		if(!lastGeneratedJobId) return;
		const url = downloadCsvUrl(lastGeneratedJobId);
		window.open(url, "_blank");

	}
	return(
		<div className="app">
			<header className="topbar">
				<div>
					<h1 className="title">Flashcard Web App</h1>
					<p className="subtitle">Upload a PDF → generate flashcards → study + download.</p>
				</div>
			</header>

			<main className="flex">
				<UploadPanel
					chunkSize={chunkSize}
					setChunkSize={setChunkSize}
					selectedFile={selectedFile}
					onChooseFile={handleChooseFile}
					onGenerate={handleGenerate}
					status={status}
					statusMessage={statusMessage}
				/>
				
				<StudyPanel
					status={status}
					statusMessage={statusMessage}
					cards={cards}
					currentIndex={currentIndex}
					currentCard={currentCard}
					showAnswer={showAnswer}
					onFlip={handleFlip}
					onNext={handleNext}
					onPrev={handlePrev}
					onDownload={handleDownload}
				/>
			</main>
		</div>
	);
}
