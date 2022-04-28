from typing import Type
import unittest
from Tutor import Tutor
from User import User

class testTutor(unittest.TestCase):

    def setUp(self):
        self.user = User("josue@techexchange.in", "Password123", "josue237")

        self.Tutor1 = Tutor("Yosemite Tee",15.00,"L","Sportswear","Men","Basic T-shirt for everyday use","../images/yosemite_tee.png", self.user)
        self.Tutor2 = Tutor("Japan Tee",25.00,"M","Casual","Men","Basic T-shirt for everyday use","../images/japan_tee.png", self.user)
        self.Tutor3 = Tutor("Blue Shirt",10.00,"S","Casual","Men","Basic T-shirt for everyday use","../images/blue_shirt.png", self.user)
        self.Tutor4 = Tutor("Black Running Jacket",25.00,"L","Sportswear","Men","Basic T-shirt for everyday use","../images/running_jacket_black.png", self.user)
        self.Tutor5 = Tutor("Spread Positive Energy Shirt",15.00,"L","Casual","Men","Basic T-shirt for everyday use","../images/spreed_energy_tee.png", self.user)
        self.Tutor6 = Tutor("White Tee",10.00,"S","Casual","Men","Basic T-shirt for everyday use","../images/white_shirt.png", self.user)
        self.Tutor7 = Tutor("Green Running Jacket",35.00,"M","Casual","Men","Basic T-shirt for everyday use","../images/running_jacket_green.png", self.user)

    def test00_init(self):
        self.assertEqual(self.Tutor1.name, "Yosemite Tee")
        self.assertEqual(self.Tutor2.price, 25.00)
        self.assertEqual(self.Tutor3.size, "S")
        self.assertEqual(self.Tutor4.style, "Sportswear")
        self.assertEqual(self.Tutor5.gender, "Men")
        self.assertEqual(self.Tutor6.description, "Basic T-shirt for everyday use")
        self.assertEqual(self.Tutor7.image, "../images/running_jacket_green.png")
        self.assertEqual(self.Tutor7.username, self.user.get_username())
    def test01_init_types(self):
        self.assertRaises(TypeError, Tutor, False,0.00,"XXS","aa","Men","aa","aa",self.user)
        self.assertRaises(TypeError, Tutor, "aa",0,"XS","aa","aa","Women","aa",self.user)
        self.assertRaises(TypeError, Tutor, "aa",0.00,False,"aa","Men","aa","aa",self.user)
        self.assertRaises(TypeError, Tutor, "aa",0.00,"S",False,"Women","aa","aa",self.user)
        self.assertRaises(TypeError, Tutor, "aa",0.00,"M","aa",False,"aa","aa",self.user)
        self.assertRaises(TypeError, Tutor, "aa",0.00,"L","aa","Men",False,"aa",self.user)
        self.assertRaises(TypeError, Tutor, "aa",0.00,"XL","aa","Women","aa",False,self.user)
        self.assertRaises(TypeError, Tutor, "aa",0.00,"XXL","aa","Men","aa","aa",False)
    def test02_init_values(self):
        self.assertRaises(ValueError, Tutor, "",0.00,"XXS","aa","Men","aa","aa",self.user)  # String len
        self.assertRaises(ValueError, Tutor, "aa",-1337.00,"XS","aa","Women","aa","aa",self.user)  # Negative number
        self.assertRaises(ValueError, Tutor, "aa",0.00,"S","aa","chair","aa","aa",self.user)  # Gender
        self.assertRaises(ValueError, Tutor, "aa",0.00,"plant","aa","Men","aa","aa",self.user)  # Size