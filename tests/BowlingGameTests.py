'''
Created on Jun 12, 2015

@author: Luca
'''

from app.BowlingGame import *
from types import MethodType
from nose.tools import assert_raises, assert_equal

class mock:
    pass


class BowlingGameTest:  
    
    def test_Roll_1_is_valued_1(self):
        roll = Roll(1)
        assert_equal(1, roll.value())
        
    def test_Roller_first_roll_value_is_valued_between_0_and_10(self):
        roller = Roller()
        roll = roller.roll_first()
        assert roll.value() >= 0 and roll.value() < 11
        
    def test_Roller_second_roll_value_is_valued_between_0_and_10_minus_first_roll_less_then_10(self):
        roller = Roller(FixedRollfactory(7))
        roll1 = roller.roll_first()
        
        roll2 = roller.roll_second()
        assert roll2.value() >= 0 and roll2.value() < 11 - roll1.value()        

    def test_first_roll_is_10_second_should_raise(self):
        roller = Roller(FixedRollfactory(10))
        roller.roll_first()
        
        assert_raises(InvalidRollError, roller.roll_second)
        
    def test_you_cant_second_roll_if_you_dont_first_roll(self):
        roller = Roller()
        assert_raises(InvalidRollError, roller.roll_second)
        
    def test_two_rolls_doesnt_sum_ten_in_frame_returns_an_open_game(self):
        roller = mock()
        roller.roll_first = MethodType(lambda slf: Roll(4), roller)
        roller.roll_second = MethodType(lambda slf: Roll(5), roller)
        
        frameRoller = FrameRoller(roller)
        assert type(frameRoller.roll()) == OpenGameFrame
        
    def test_two_rolls_that_sums_ten_in_frame_returns_a_spare(self):
        roller = mock()
        roller.roll_first = MethodType(lambda slf: Roll(4), roller)
        roller.roll_second = MethodType(lambda slf: Roll(6), roller)
        
        frameRoller = FrameRoller(roller)
        assert type(frameRoller.roll()) == SpareFrame
        
    def test_one_roll_that_values_10_in_a_frame_return_strike(self):
        roller = mock()
        roller.roll_first = MethodType(lambda slf: Roll(10), roller)
    
        frameRoller = FrameRoller(roller)
        assert type(frameRoller.roll()) == StrikeFrame
        
    def test_bowling_game_should_roll_ten_frames(self):
        frameRoller = mock()
        frameRoller.i = 0
        def f(slf, i): slf.i = slf.i + 1        
        frameRoller.roll = MethodType(f, frameRoller)
        
        bg = BowlingGame(frameRoller)
        bg.play()
        assert frameRoller.i == 10 
        
    def test_ten_open_game_roll_1_1_must_sums_up_to_20(self):
        frameRoller = mock()        
        frameRoller.roll = MethodType(lambda slf, i: OpenGameFrame(Roll(1), Roll(1)), frameRoller)
        
        bg = BowlingGame(frameRoller)
        result = bg.play()
        
        assert result.sums_up() == 20
        
    def test_an_open_game_shouldnt_ask_for_any_roll(self):
        frame = OpenGameFrame(Roll(1), Roll(1))
        result = mock()
        result.i = 0
        def f(slf): slf.i = slf.i + 1
        result.give_me_a_roll = MethodType(f, result)
        
        frame.value(result)
        
        assert_equal(0, result.i)
        
    def test_a_spare_should_ask_for_1_roll(self):
        frame = SpareFrame(Roll(1))
        result = mock()
        result.i = 0
        def f(slf): 
            slf.i = slf.i + 1
            return Roll(5)
        result.give_me_a_roll = MethodType(f, result)
        
        frame.value(result)
                
        assert_equal(1, result.i)
        
    def test_a_strike_should_ask_for_2_roll(self):
        frame = StrikeFrame()
        result = mock()
        result.i = 0
        def f(slf, reset): 
            slf.i = slf.i + 1
            return Roll(5)
        result.give_me_a_roll = MethodType(f, result)
        
        frame.value(result)
                
        assert_equal(2, result.i)        

    def test_a_spare_should_be_valued_10_plus_1_roll_value(self):        
        frame = SpareFrame(Roll(2))
        result = mock()
        result.give_me_a_roll = MethodType(lambda slf: Roll(3), result)
        
        val = frame.value(result)
                
        assert_equal(13, val)
        
    def test_a_strike_should_be_valued_10_plus_2_rolls_value(self):        
        frame = StrikeFrame()
        result = mock()
        result.give_me_a_roll = MethodType(lambda slf, reset: Roll(3), result)
        
        val = frame.value(result)
                
        assert_equal(16, val)
        
    def test_a_strike_should_fail_if_asked_for_value_and_followed_only_by_another_strike(self):
        frames = [StrikeFrame(), StrikeFrame()]
        result = BowlingGameResult(frames)
        assert_raises(IndexError, frames[0].value, result)
        
    def test_a_strike_asked_for_value_and_followed_by_another_frame_should_success(self):
        frames = [StrikeFrame(), OpenGameFrame(Roll(2), Roll(4))]
        result = BowlingGameResult(frames)
        assert_equal(16, frames[0].value(result))
        
    def test_a_strike_asked_for_value_and_followed_only_by_another_strike_and_another_frame_should_success(self):
        frames = [StrikeFrame(), StrikeFrame(), SpareFrame(Roll(9))]
        result = BowlingGameResult(frames)
        assert_equal(29, frames[0].value(result))
        
    def test_result_sums(self):
        frames_master = [[StrikeFrame(), StrikeFrame(), StrikeFrame(), SpareFrame(Roll(9)), OpenGameFrame(Roll(2), Roll(4))],
                         [SpareFrame(Roll(6)), StrikeFrame(), OpenGameFrame(Roll(3), Roll(2)), OpenGameFrame(Roll(2), Roll(4))],
                         [SpareFrame(Roll(6)), StrikeFrame(), StrikeFrame(), StrikeFrame(), LastFrame(Roll(6), Roll(4), Roll(6))]]
        
        results = [30 + 29 + 20 + 12 + 6, 20 + 15 + 5 + 6, 20 + 30 + 26 + 20 + 16]        
        
        def get_game_value(frames, result_value):
            result = BowlingGameResult(frames)
            assert_equal(result_value, result.sums_up())
        
        for frames, result in zip(frames_master, results):
            yield get_game_value, frames, result
        
        
    def test_tenth_frame_roll_shoud_return_last_frame(self):
        roller = mock()
        roller.roll_first = MethodType(lambda slf: Roll(4), roller)
        roller.roll_second = MethodType(lambda slf: Roll(6), roller)
        
        frameRoller = FrameRoller(roller)
        assert_equal(LastFrame, type(frameRoller.roll(10)))
        
    def test_tenth_frame_roll_with_strike_shoud_call_first_roll_twice(self):
        def f(slf): 
            slf.i = slf.i + 1
            return Roll(10)
        
        roller = mock()
        roller.i = 0
        roller.roll_first = MethodType(f, roller)
        roller.roll_second = MethodType(lambda slf: Roll(0), roller)            
            
        frameRoller = FrameRoller(roller)
        frameRoller.roll(10)
        assert_equal(2, roller.i)
        
    def test_tenth_frame_roll_with_strike_shoud_call_second_roll_zero_times(self):
        def f(slf): 
            slf.i = slf.i + 1
            return Roll(0)
        
        roller = mock()
        roller.i = 0
        roller.roll_first = MethodType(lambda slf: Roll(10), roller)
        roller.roll_second = MethodType(f, roller)            
            
        frameRoller = FrameRoller(roller)
        frameRoller.roll(10)
        assert_equal(0, roller.i)
        
    def test_tenth_frame_roll_with_spare_shoud_call_second_roll_one_time(self):
        def f(slf): 
            slf.i = slf.i + 1
            return Roll(4)
        
        roller = mock()
        roller.i = 0
        roller.roll_first = MethodType(lambda slf: Roll(6), roller)
        roller.roll_second = MethodType(f, roller)            
            
        frameRoller = FrameRoller(roller)
        frameRoller.roll(10)
        assert_equal(1, roller.i)
        
    def test_tenth_frame_roll_with_spare_shoud_call_first_roll_twice(self):
        def f(slf): 
            slf.i = slf.i + 1
            return Roll(4)
        
        roller = mock()
        roller.i = 0
        roller.roll_first = MethodType(f, roller)
        roller.roll_second = MethodType(lambda slf: Roll(6), roller)            
            
        frameRoller = FrameRoller(roller)
        frameRoller.roll(10)
        assert_equal(2, roller.i)
        
    def test_tenth_frame_roll_with_opengame_shoud_call_first_roll_one_time(self):
        def f(slf): 
            slf.i = slf.i + 1
            return Roll(4)
        
        roller = mock()
        roller.i = 0
        roller.roll_first = MethodType(f, roller)
        roller.roll_second = MethodType(lambda slf: Roll(3), roller)            
            
        frameRoller = FrameRoller(roller)
        frameRoller.roll(10)
        assert_equal(1, roller.i)       
    
        
    def test_bowling_game_last_frame(self):
        roller = mock()
        roller.roll_first = MethodType(lambda slf: Roll(5), roller)
        roller.roll_second = roller.roll_first 
        frameRoller = FrameRoller(roller)
        
        bg = BowlingGame(frameRoller)
        result = bg.play()
        assert_equal(LastFrame, type(result.frames[-1]))
        