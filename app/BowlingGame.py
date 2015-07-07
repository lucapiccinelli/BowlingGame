class InvalidRollError(Exception):
    pass

class Roll(object):    
    def __init__(self, value):
        self._value = value
        
    def value(self):
        return self._value
    

from random import Random


class RandomRollfactory():
    def create(self, first_roll = Roll(0)):
        return Roll(Random().randint(0, 10 - first_roll.value()))
    

class FixedRollfactory():
    def __init__(self, value):
        self.value = value
    
    def create(self, first_roll = Roll(0)):
        return Roll(self.value)
    

class Roller():
    def __init__(self, first_roll_factory = RandomRollfactory(), second_roll_factory = RandomRollfactory()):
        self.first_roll_factory = first_roll_factory
        self.second_roll_factory = second_roll_factory
        
    def roll_first(self):
        self.first_roll = self.first_roll_factory.create()         
        return self.first_roll
    
    def roll_second(self):
        if not hasattr(self, 'first_roll'):
            raise InvalidRollError('You must roll the first_roll before rolling the second')
            
        if self.first_roll.value() == 10:
            raise InvalidRollError('first roll is strike, you can\'t roll again in this frame')
        
        return self.second_roll_factory.create(self.first_roll)


class FrameRoller(object):    
    def __init__(self, roller):
        self.roller = roller

    def roll(self, idx = 0):
        if(idx == 10):
            roll1 = self.roller.roll_first()
            if roll1.value() == 10:
                roll2 = self.roller.roll_first()
                return LastFrame(roll1, roll2)
            else:
                roll2 = self.roller.roll_second()
                roll3 = Roll(0)
                if roll1.value() + roll2.value() == 10:
                    roll3 = self.roller.roll_first()
                return LastFrame(roll1, roll2, roll3)
        
        
        roll1 = self.roller.roll_first()
        if roll1.value() == 10:
            return StrikeFrame()
        
        roll2 = self.roller.roll_second()
        
        if roll1.value() + roll2.value() < 10:
            return OpenGameFrame(roll1, roll2)
        else:
            return SpareFrame(roll1)       


class LastFrame(object):
    def __init__(self, roll1, roll2, roll3 = Roll(0)):
        self.roll1 = roll1
        self.roll2 = roll2
        self.roll3 = roll3
        self.rolls =  [self.roll1, self.roll2, self.roll3]
        self.roll_idx = 0
        
    def value(self, bowlingGameResult):
        if self.roll1.value() == 10:
            return self.roll1.value() + self.roll2.value() + self.roll2.value()
        return self.roll1.value() + self.roll2.value() + self.roll3.value()

    def give_me_your_roll(self, reset_frame):
        if reset_frame: self.roll_idx = 0
        
        roll = self.rolls[self.roll_idx]
        self.roll_idx = self.roll_idx + 1
        return (roll, 0)
    
    def __str__(self):
        return '|{0},{1},{2}|'.format(self.roll1.value(), self.roll2.value(), self.roll3.value())

class OpenGameFrame(object):
    def __init__(self, roll1, roll2):
        self.roll1 = roll1
        self.roll2 = roll2
        self.rolls =  [self.roll1, self.roll2]
        self.roll_idx = 0
        
    def value(self, bowlingGameResult):
        return self.roll1.value() + self.roll2.value()
    
    def give_me_your_roll(self, reset_frame):
        if reset_frame: self.roll_idx = 0
        
        roll = self.rolls[self.roll_idx]
        self.roll_idx = self.roll_idx + 1
        return (roll, 0)
    
    def __str__(self):
        return '|{0},{1}|'.format(self.roll1.value(), self.roll2.value())

class SpareFrame(object):
    def __init__(self, roll1):
        self.roll1 = roll1
        self.roll2 = Roll(10 - roll1.value())
        self.rolls =  [self.roll1, self.roll2]
        self.roll_idx = 0
        
    def value(self, bowlingGameResult):
        roll = bowlingGameResult.give_me_a_roll()
        return self.roll1.value() + self.roll2.value() + roll.value()
    
    def give_me_your_roll(self, reset_frame):
        if reset_frame: self.roll_idx = 0
        
        roll = self.rolls[self.roll_idx]
        self.roll_idx = self.roll_idx + 1
        return (roll, self.roll_idx - 1)
    
    def __str__(self):
        return '|{0},{1}!|'.format(self.roll1.value(), self.roll2.value())

class StrikeFrame(object):
    def __init__(self):
        self.roll1 = Roll(10)
        
    def value(self, bowlingGameResult):
        roll1 = bowlingGameResult.give_me_a_roll(True)
        roll2 = bowlingGameResult.give_me_a_roll(False)
        
        return self.roll1.value() + roll1.value() + roll2.value()
    
    def give_me_your_roll(self, reset_frame):
        return (self.roll1, 1)
    
    def __str__(self):
        return '|{0}!!!|'.format(self.roll1.value())    
        
class BowlingGame(object):
    def __init__(self, frameRoller):
        self.frameRoller = frameRoller
    
    def play(self):        
        return BowlingGameResult([self.frameRoller.roll(i) for i in range(1, 11)])
    
class BowlingGameResult():
    def __init__(self, frames):
        self.frames = frames
        self.frame_idx = 0
        self.roll_idx = 1
    
    def sums_up(self):
        def f(frame):
            val = frame.value(self)        
            self.frame_idx = self.frame_idx + 1
            self.roll_idx = 1
            
            return val
                        
        return sum(map(f, self.frames))
    
    def give_me_a_roll(self, reset_frame = True):
        roll, roll_idx_add = self.frames[self.frame_idx + self.roll_idx].give_me_your_roll(reset_frame)
        self.roll_idx = self.roll_idx + roll_idx_add
        
        return roll
    
    def __str__(self):
        out_str = 'TOTALE: {0}\n'.format(self.sums_up())
        for frame in self.frames:
            out_str = out_str + str(frame)
            
        return out_str
            
            
if __name__ == '__main__':
    game = BowlingGame(FrameRoller(Roller()))
    result = game.play()
    print(result)
    
    
    
    
    