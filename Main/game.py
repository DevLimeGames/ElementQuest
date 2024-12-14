import json
import os

def readability(func):
    def wrapper(*args, **kwargs):
        print('')
        print('------------------------------------')
        result = func(*args, **kwargs)
        print('------------------------------------')
        print('')
        
        return result
        
    return wrapper
 
class Character:
    def __init__(self, starting_location):
        self.location = starting_location
        
        self.exp = 0
        self.level = 1
        
        self.stats_point = 0
        
        self.stats = {
            'Attack': 1,
            'Magic': 1,
            'Defense': 1
        }
    
    @readability
    def Spend_stats(self):
        print(f'Stats: {self.stats_point}')
        for stat in self.stats.keys():
            print(f'{stat}: {self.stats[stat]}')
        print('')
        
        stats = input('Stats: ')
        try:
            spend = int(input('How many: '))
        except:
            print('Inavalid Character')
            return
        
        count = 1
        for stat in self.stats.keys():
            if stat.lower() == stats.lower():
                if spend <= self.stats_point:
                    self.stats[stats.lower().capitalize()] += spend
                    self.stats_point -= spend
                
                    print(f'Succesful {stats.lower().capitalize()}: {self.stats[stats.lower().capitalize()]}')
                    
                    return
                else:
                    print('Not enough stat points')
                       
                    return
            else:
                if count == len(self.stats.keys()):
                    print('Stat selected not found')
                    
            count += 1
    
    @readability
    def fight(self, mob):
        if 'Boss' in mob.type:
            health = mob.level
        else:
            health = mob.level / 2
            
        self.health = self.stats['Defense'] * 5
        
        while True:
            health -= self.stats['Attack'] + self.stats['Magic']
            self.health -= mob.level / 4
            
            if self.health <= 0:
                break
            
            if health <= 0:
                self.win_against(mob)
                break
                
            print(f'Your Health: {self.health}')
            print(f'Enemy Health: {health}')
            
            input('Continue: ')
            print('')

    def win_against(self, mob):
        exp_needed = self.level ** 2 * 5
        exp_gained = (mob.level ** 2) // 1.5

        self.exp += exp_gained
        print(f'You gained {exp_gained} experience points!')

        while self.exp >= exp_needed:
            self.exp -= exp_needed
            self.level += 1
            self.stats_point += 3
            exp_needed = self.level ** 2 * 22
            print(f'Congratulations! You have reached level {self.level}!')

        return exp_gained
        
class Enemy:
    def __init__(self, name, level, lvl_need, type):
        self.name = name
        self.level = level
        self.level_needed = lvl_need
        self.type = type
    
    def return_json(self):
        return {
            'name': self.name,
            'level': self.level,
            'lvl_need': self.level_needed,
            'type': self.type
        }
    
    def update_json(self, data):
        self.name = data['name']
        self.level = data['level']
        self.level_needed = data['lvl_need']
        self.type = data['type']

class Location:
    def __init__(self, name, mobs):
        self.name = name
        self.mobs = []
        for mob in mobs:
            if isinstance(mob, Enemy):
                self.mobs.append(mob)
            else:
                raise ValueError('All mobs must be instances of the Enemy class.')

    def return_json(self):
        mobs_json = []
        for mob in self.mobs:
            mobs_json.append(mob.return_json())
        return {
            'name': self.name,
            'mobs': mobs_json
        }
    
    def update_json(self, data):
        self.name = data['name']
        self.mobs = []
        for mob_data in data['mobs']:
            self.mobs.append(Enemy(mob_data['name'], mob_data['level'], mob_data['lvl_need'], mob_data['type']))

class Game:
    def __init__(self):
        self.locations = self.load_locations()
        self.location_dict = {loc.name: loc for loc in self.locations}
        self.player = Character(self.location_dict['Starter Island'])
        self.playing = True
        self.actions = {
            'farm': self.farm,
            'travel': self.travel,
            'stats': self.player.Spend_stats
        }

    def load_locations(self):
        file_path = './files/Locations.json'
        locations = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                for location_data in data['locations']:
                    mobs = [Enemy(mob['name'], mob['level'], mob['lvl_need'], mob['type']) for mob in location_data['mobs']]
                    location = Location(location_data['name'], mobs)
                    locations.append(location)
        else:
            print(f"File not found: {file_path}")
        return locations
    
    @readability
    def farm(self):
        print(f'{self.player.location.name}:')
        
        available = []
        for mob in self.player.location.mobs:
            print(f'{mob.level_needed} - {mob.name}: {mob.level} ({",".join(mob.type)})')
            available.append(mob.name.lower())
            
        print('')
        select = input('Select: ')
        
        if select.lower() in available:
            for mob in self.player.location.mobs:
                if mob.name.lower() == select.lower():
                    if self.player.level >= mob.level_needed:       
                        self.player.fight(mob)
                    else:
                        print('Low Level cannot fight this mob')
    
    @readability
    def travel(self):
        for loc in self.location_dict.keys():
            print(loc)
            
        travel = input('Travel To: ').lower()
        
        for location in self.location_dict.keys():
            if travel == location.lower():
                self.player.location = self.location_dict[location]
            
    def execute(self):
        while self.playing:
            feed = input('Action: ').strip().lower()
            if feed in self.actions:
                self.actions[feed]()
            elif feed == '.edit':
                c = input('Command: ').lower()
                s = input('Shortcut: ')
                
                if c in self.actions.keys():
                    self.actions[s] = self.actions[c]
            else:
                print('')
                print('Unknown command.')
                print('')
                
if __name__ == '__main__':
    game = Game()
    game.execute()