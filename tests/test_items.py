"""Tests for the item and equipment system."""

import pytest
from myrpg.items import (
    ItemRarity, EquipmentSlot,
    Weapon, WeaponClass, create_weapon,
    Armor, ArmorWeight, create_armor,
    Material,
    Inventory, EquipmentLoadout,
    LootTable, DropManager,
)
from myrpg.combat import ThemeType


class TestWeapons:
    def test_create_weapon(self):
        sword = create_weapon(WeaponClass.SWORD, tier=1, rarity=ItemRarity.COMMON)
        assert sword.name == "Steel Sword"
        assert sword.weapon_class == WeaponClass.SWORD
        assert sword.required_theme == ThemeType.ARMED

    def test_weapon_damage_scales_with_rarity(self):
        common = create_weapon(WeaponClass.SWORD, tier=1, rarity=ItemRarity.COMMON)
        rare = create_weapon(WeaponClass.SWORD, tier=1, rarity=ItemRarity.RARE)
        assert rare.effective_damage > common.effective_damage

    def test_weapon_theme_requirements(self):
        bow = create_weapon(WeaponClass.BOW)
        assert bow.required_theme == ThemeType.RANGED
        assert bow.can_equip(ThemeType.RANGED)
        assert not bow.can_equip(ThemeType.ARMED)

    def test_weapon_characteristics(self):
        dagger = create_weapon(WeaponClass.DAGGER)
        hammer = create_weapon(WeaponClass.HAMMER)
        assert dagger.speed_modifier > hammer.speed_modifier
        assert hammer.damage_modifier > dagger.damage_modifier


class TestArmor:
    def test_create_armor(self):
        chest = create_armor(
            EquipmentSlot.BODY,
            ArmorWeight.HEAVY,
            tier=2,
            rarity=ItemRarity.UNCOMMON,
        )
        assert "Plate" in chest.name
        assert chest.slot == EquipmentSlot.BODY

    def test_armor_weight_affects_stats(self):
        cloth = create_armor(EquipmentSlot.BODY, ArmorWeight.CLOTH)
        plate = create_armor(EquipmentSlot.BODY, ArmorWeight.HEAVY)
        assert plate.defense_modifier > cloth.defense_modifier
        assert plate.speed_penalty > cloth.speed_penalty


class TestInventory:
    def test_add_item(self):
        inv = Inventory()
        sword = create_weapon(WeaponClass.SWORD)
        assert inv.add(sword)
        assert inv.count == 1

    def test_inventory_capacity(self):
        inv = Inventory()
        inv._capacity = 2
        inv.add(create_weapon(WeaponClass.SWORD))
        inv.add(create_weapon(WeaponClass.DAGGER))
        assert inv.is_full
        assert not inv.add(create_weapon(WeaponClass.AXE))

    def test_sell_item(self):
        inv = Inventory()
        sword = create_weapon(WeaponClass.SWORD)
        inv.add(sword)
        gold = inv.sell_item(sword)
        assert gold > 0
        assert inv.count == 0

    def test_get_equipment(self):
        inv = Inventory()
        inv.add(create_weapon(WeaponClass.SWORD))
        inv.add(create_armor(EquipmentSlot.BODY, ArmorWeight.MEDIUM))
        equipment = inv.get_equipment()
        assert len(equipment) == 2


class TestEquipmentLoadout:
    def test_equip_item(self):
        loadout = EquipmentLoadout()
        sword = create_weapon(WeaponClass.SWORD)
        loadout.equip(sword, ThemeType.ARMED)
        assert loadout.get(EquipmentSlot.MAIN_HAND) == sword

    def test_equip_replaces_previous(self):
        loadout = EquipmentLoadout()
        sword1 = create_weapon(WeaponClass.SWORD)
        sword2 = create_weapon(WeaponClass.DAGGER)

        loadout.equip(sword1, ThemeType.ARMED)
        previous = loadout.equip(sword2, ThemeType.ARMED)

        assert previous == sword1
        assert loadout.get(EquipmentSlot.MAIN_HAND) == sword2

    def test_cannot_equip_wrong_theme(self):
        loadout = EquipmentLoadout()
        bow = create_weapon(WeaponClass.BOW)

        with pytest.raises(ValueError):
            loadout.equip(bow, ThemeType.ARMED)

    def test_total_stats(self):
        loadout = EquipmentLoadout()
        sword = create_weapon(WeaponClass.SWORD, tier=2)
        armor = create_armor(EquipmentSlot.BODY, ArmorWeight.MEDIUM, tier=2)

        loadout.equip(sword, ThemeType.ARMED)
        loadout._slots[EquipmentSlot.BODY] = armor

        stats = loadout.get_total_stats()
        assert stats.power_bonus > 0
        assert stats.health_bonus > 0


class TestLootSystem:
    def test_loot_table_generates_items(self):
        table = LootTable(tier=1)
        table.seed(42)

        drops = []
        for _ in range(20):
            drop = table.generate_drop("test")
            if drop:
                drops.append(drop)

        assert len(drops) > 0

    def test_higher_tier_better_rarity(self):
        low_tier = LootTable(tier=1)
        high_tier = LootTable(tier=5)

        low_tier.seed(42)
        high_tier.seed(42)

        low_rarities = []
        high_rarities = []

        for _ in range(100):
            low_drop = low_tier.generate_drop()
            high_drop = high_tier.generate_drop()
            if low_drop:
                low_rarities.append(low_drop.item.rarity.value)
            if high_drop:
                high_rarities.append(high_drop.item.rarity.value)

        # Higher tier should have more non-common items
        low_non_common = sum(1 for r in low_rarities if r != "common")
        high_non_common = sum(1 for r in high_rarities if r != "common")
        assert high_non_common >= low_non_common

    def test_drop_manager_mob_drops(self):
        dm = DropManager(base_drop_chance=1.0)  # Guaranteed drops
        drop = dm.roll_mob_drop(tier=1, source="Test Mob")
        assert drop is not None
        assert dm.total_drops == 1

    def test_drop_manager_boss_drops(self):
        dm = DropManager()
        drops = dm.roll_boss_drop(tier=2, source="Test Boss")
        assert len(drops) >= 2  # Bosses drop 2-4 items
