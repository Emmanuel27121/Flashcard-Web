
export default function StudyPanel({
    status,
    statusMessage,
    cards,
    currentIndex,
    currentCard,
    showAnswer,
    onFlip,
    onNext,
    onPrev,
    onDownload,
}){
    const isWorking = status === "working";
    const hasCards = cards.length > 0;

    return(
        <section className="panel">
            <div className="panelHeader">
                <div>
                    <h2>Study</h2>
                    <p className="muted">Flip cards, move next/prev, and download when ready.</p>
                </div>

                <button className="secondaryBtn" disabled={!hasCards} onClick={onDownload}>Download CSV</button>
            </div>

            {!isWorking && !hasCards && (
                <div className="emptyState">
                    <div className="emptyTitle">No deck yet</div>
                    <div className="muted">Upload a PDF and generate flashcards to start studying</div>
                </div>
            )}

            {isWorking && (
                <div className="loadingState">
                    <div className="skeletonCard" />
                    <div className="muted" style={{marginTop: 10}}>
                        {statusMessage || "Preparing your flashcards..."}
                    </div>
                </div>
            )}

            {!isWorking && hasCards && (
                <>
                    <div className="StudyTop">
                        <div className="pill">
                            Card <b>{currentIndex + 1}</b> / {cards.length}
                        </div>
                        <div className="pill muted">Click the card to flip</div>
                    </div>

                    <div className="flashcard" onClick={onFlip}>
                        <div className="label">{showAnswer ? "Answer" : "Question"}</div>
                        <div className="content">
                            {showAnswer ? currentCard?.answer : currentCard?.question}
                        </div>
                        <div className="hint">Click to flip</div>
                    </div>

                    <div className="controls">
                        <button className="secondaryBtn" onClick={onPrev} disabled={currentIndex === 0}>
                            Previous
                        </button>
                        
                        <button className="secondaryBtn" onClick={onFlip}>
                            {showAnswer ? "Show Question" : "Show Answer"}
                        </button>

                        <button className="secondaryBtn" onClick={onNext} disabled={currentIndex === cards.length - 1}>
                            Next
                        </button>
                    </div>
                </>
                )}
        </section>
    );
}



