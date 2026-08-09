-- 推箱子核心逻辑（Haskell 教学）
module Game
  ( GameState(..)
  , fromRows
  , tryMove
  , undo
  , renderAscii
  ) where

import Data.List (foldl')
import Data.Set (Set)
import qualified Data.Set as Set

type Pos = (Int, Int)
type Cell = String

data Hist = Hist
  { hPlayer :: Pos
  , hBoxFrom :: Maybe Cell
  , hBoxTo :: Maybe Cell
  } deriving (Show)

data GameState = GameState
  { walls :: Set Cell
  , goals :: Set Cell
  , boxes :: Set Cell
  , player :: Pos
  , moves :: Int
  , won :: Bool
  , width :: Int
  , height :: Int
  , levelIndex :: Int
  , hist :: [Hist]
  } deriving (Show)

key :: Int -> Int -> Cell
key x y = show x ++ "," ++ show y

fromRows :: [String] -> Int -> GameState
fromRows rows idx =
  let cells = [ (x, y, ch)
              | (y, row) <- zip [0..] rows
              , (x, ch) <- zip [0..] row
              ]
      maxX = maximum (0 : [x | (x, _, _) <- cells])
      maxY = maximum (0 : [y | (_, y, _) <- cells])
      go (ws, gs, bs, pl) (x, y, ch) =
        let k = key x y
        in case ch of
             '#' -> (Set.insert k ws, gs, bs, pl)
             '.' -> (ws, Set.insert k gs, bs, pl)
             '$' -> (ws, gs, Set.insert k bs, pl)
             '*' -> (ws, Set.insert k gs, Set.insert k bs, pl)
             '@' -> (ws, gs, bs, (x, y))
             '+' -> (ws, Set.insert k gs, bs, (x, y))
             _   -> (ws, gs, bs, pl)
      (ws, gs, bs, pl) = foldl' go (Set.empty, Set.empty, Set.empty, (0, 0)) cells
  in GameState ws gs bs pl 0 False (maxX + 1) (maxY + 1) idx []

checkWin :: Set Cell -> Set Cell -> Bool
checkWin bs gs = all (`Set.member` gs) (Set.toList bs)

tryMove :: Int -> Int -> GameState -> GameState
tryMove dx dy s
  | won s = s
  | Set.member nk (walls s) = s
  | Set.member nk (boxes s) =
      let bx = nx + dx
          by = ny + dy
          bk = key bx by
      in if Set.member bk (walls s) || Set.member bk (boxes s)
           then s
           else
             let boxes' = Set.insert bk (Set.delete nk (boxes s))
                 moves' = moves s + 1
             in s
               { boxes = boxes'
               , player = (nx, ny)
               , moves = moves'
               , won = checkWin boxes' (goals s)
               , hist = Hist (player s) (Just nk) (Just bk) : hist s
               }
  | otherwise =
      s
        { player = (nx, ny)
        , hist = Hist (player s) Nothing Nothing : hist s
        }
  where
    (px, py) = player s
    nx = px + dx
    ny = py + dy
    nk = key nx ny

undo :: GameState -> GameState
undo s
  | won s || null (hist s) = s
  | otherwise = go (hist s) (player s)
  where
    go [] pl = s { player = pl, hist = [] }
    go (h:rest) pl =
      case hBoxFrom h of
        Nothing -> go rest (hPlayer h)
        Just bf ->
          let bt = maybe bf id (hBoxTo h)
              boxes' = Set.insert bf (Set.delete bt (boxes s))
          in s
            { player = hPlayer h
            , boxes = boxes'
            , moves = max 0 (moves s - 1)
            , won = False
            , hist = rest
            }

renderAscii :: GameState -> String
renderAscii s = unlines
  [ [ cell x y | x <- [0 .. width s - 1] ]
  | y <- [0 .. height s - 1]
  ]
  where
    cell x y
      | player s == (x, y) = if Set.member k (goals s) then '+' else '@'
      | Set.member k (boxes s) = if Set.member k (goals s) then '*' else '$'
      | Set.member k (walls s) = '#'
      | Set.member k (goals s) = '.'
      | otherwise = ' '
      where
        k = key x y
