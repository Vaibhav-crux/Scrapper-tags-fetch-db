from fastapi import FastAPI

from app.routers import (forbes, ambCrypto, blockWorks, coinDesk, coinGape, coinTelegraph, cryptoPotato, watcherGuru, beInCrypto, theDefiant)

app = FastAPI()

app.include_router(forbes.router)
app.include_router(ambCrypto.router)
app.include_router(watcherGuru.router)
app.include_router(blockWorks.router)
app.include_router(coinDesk.router)
app.include_router(coinGape.router)
app.include_router(coinTelegraph.router)
app.include_router(cryptoPotato.router)
app.include_router(beInCrypto.router)
app.include_router(theDefiant.router)

