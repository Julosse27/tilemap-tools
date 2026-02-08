"""Fonctions principales pour manipuler les tilemaps"""

class Tilemap:
    def __init__(self, width, height, default_tile=0):
        self.width = width
        self.height = height
        self.map = [[default_tile for _ in range(width)] for _ in range(height)]
    
    def set_tile(self, x, y, tile_id):
        """Définit une tile à une position donnée"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map[y][x] = tile_id
        else:
            raise ValueError(f"Position ({x}, {y}) hors limites")
    
    def get_tile(self, x, y):
        """Récupère la tile à une position donnée"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map[y][x]
        raise ValueError(f"Position ({x}, {y}) hors limites")
    
    def save_csv(self, filename):
        """Sauvegarde la tilemap en CSV"""
        with open(filename, 'w') as f:
            for row in self.map:
                f.write(','.join(map(str, row)) + '\n')
    
    def save_json(self, filename):
        """Sauvegarde la tilemap en JSON"""
        import json
        data = {
            'width': self.width,
            'height': self.height,
            'tiles': self.map
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_csv(filename):
        """Charge une tilemap depuis un CSV"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        map_data = []
        for line in lines:
            row = [int(x.strip()) for x in line.strip().split(',') if x.strip()]
            if row:
                map_data.append(row)
        
        if not map_data:
            raise ValueError("Fichier CSV vide")
        
        height = len(map_data)
        width = len(map_data[0])
        
        tilemap = Tilemap(width, height)
        tilemap.map = map_data
        return tilemap
    
    @staticmethod
    def load_json(filename):
        """Charge une tilemap depuis un JSON"""
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        
        tilemap = Tilemap(data['width'], data['height'])
        tilemap.map = data['tiles']
        return tilemap