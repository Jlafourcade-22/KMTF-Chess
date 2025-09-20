from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chess
import chess.engine
import time

app = FastAPI(title="Stockfish Analysis API")

class AnalyzeRequest(BaseModel):
    fen: str
    depth: int = 15            # default search depth
    movetime_ms: int = None    # if provided, overrides depth
    multipv: int = 1           # number of PV lines (set >1 if you want alternatives)

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # Validate FEN
    try:
        board = chess.Board(req.fen)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid FEN")

    engine_path = "/usr/bin/stockfish"  # default path in the Docker image below
    try:
        # Start Stockfish (pops a subprocess)
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            # choose limit (time or depth)
            if req.movetime_ms:
                limit = chess.engine.Limit(time=req.movetime_ms / 1000.0)
            else:
                limit = chess.engine.Limit(depth=req.depth)

            start = time.time()
            # multipv controls how many PVs Stockfish returns; keep it small for demos
            info = engine.analyse(board, limit, multipv=req.multipv)
            elapsed_ms = int((time.time() - start) * 1000)

            # info is a dict (for multipv=1). Parse score & PV
            score = info["score"].white()
            if score.is_mate():
                eval_obj = {"type": "mate", "value": score.mate()}  # positive => mate for White
            else:
                cp = score.score()
                eval_obj = {"type": "cp", "value": cp, "eval": cp / 100.0}

            pv_moves = None
            if "pv" in info and info["pv"]:
                pv_moves = [m.uci() for m in info["pv"]]
                bestmove = pv_moves[0]
            else:
                # fallback - ask engine for a move
                play = engine.play(board, limit)
                bestmove = play.move.uci()

            depth_returned = info.get("depth", req.depth)

            return {
                "eval": eval_obj,
                "bestmove": bestmove,
                "pv": pv_moves,
                "depth": depth_returned,
                "time_ms": elapsed_ms
            }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Stockfish binary not found at {engine_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
