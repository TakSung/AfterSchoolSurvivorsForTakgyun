"""
Test script to verify attack speed increases with level-ups.

This script creates a simple test to ensure that the WeaponManager
correctly handles level-up events and increases attack speed by 10% per level.
"""

from src.components.experience_component import ExperienceComponent
from src.components.player_component import PlayerComponent
from src.components.weapon_component import WeaponComponent, WeaponType
from src.core.entity_manager import EntityManager
from src.core.events.event_bus import EventBus
from src.core.events.level_up_event import LevelUpEvent
from src.core.weapon_manager import WeaponManager


def test_attack_speed_increase():
    """Test that attack speed increases by 10% per level-up."""
    print("=== 공격 속도 레벨업 테스트 ===")
    
    # ECS 구성 요소 초기화
    entity_manager = EntityManager()
    event_bus = EventBus()
    weapon_manager = WeaponManager()
    
    # WeaponManager 설정
    weapon_manager.set_entity_manager(entity_manager)
    event_bus.subscribe(weapon_manager)
    
    # 플레이어 엔티티 생성
    player_entity = entity_manager.create_entity()
    player_id = player_entity.entity_id
    
    # 플레이어 컴포넌트 추가
    entity_manager.add_component(player_entity, PlayerComponent())
    entity_manager.add_component(
        player_entity, ExperienceComponent(current_exp=0, level=1)
    )
    
    # 초기 무기 컴포넌트 (기본 공격 속도 2.0)
    initial_weapon = WeaponComponent(
        weapon_type=WeaponType.SOCCER_BALL,
        damage=25,
        attack_speed=2.0,
        range=300.0,
        last_attack_time=0.0,
    )
    entity_manager.add_component(player_entity, initial_weapon)
    
    # 초기 상태 확인
    initial_speed = weapon_manager.get_effective_attack_speed(player_entity)
    print(f"📊 레벨 1 - 공격 속도: {initial_speed:.2f}/s")
    
    # 레벨업 이벤트들 시뮬레이션
    levels_to_test = [2, 3, 4, 5]
    
    for new_level in levels_to_test:
        # 레벨업 이벤트 생성
        level_up_event = LevelUpEvent.create_from_level_change(
            player_entity_id=player_id,
            previous_level=new_level - 1,
            new_level=new_level,
            total_experience=new_level * 100,
            remaining_experience=0,
        )
        
        # 이벤트 발행 및 처리
        event_bus.publish(level_up_event)
        event_bus.process_events()
        
        # 공격 속도 확인
        current_speed = weapon_manager.get_effective_attack_speed(player_entity)
        expected_speed = 2.0 * (1.0 + (new_level - 1) * 0.1)
        
        print(f"📊 레벨 {new_level} - 공격 속도: {current_speed:.2f}/s (예상: {expected_speed:.2f}/s)")
        
        # 검증
        if abs(current_speed - expected_speed) < 0.01:
            print(f"✅ 레벨 {new_level}: 공격 속도 증가 정상")
        else:
            print(f"❌ 레벨 {new_level}: 공격 속도 증가 오류 - 실제: {current_speed:.2f}, 예상: {expected_speed:.2f}")
    
    # 최종 결과
    final_speed = weapon_manager.get_effective_attack_speed(player_entity)
    final_level = levels_to_test[-1]
    expected_final = 2.0 * (1.0 + (final_level - 1) * 0.1)
    
    print(f"\n🎯 최종 결과:")
    print(f"   레벨 {final_level}: {final_speed:.2f}/s (기본 2.0/s → +{((final_speed/2.0 - 1)*100):.0f}% 증가)")
    print(f"   예상 공식: 2.0 × (1 + (레벨-1) × 0.1) = {expected_final:.2f}/s")
    
    if abs(final_speed - expected_final) < 0.01:
        print("✅ 모든 테스트 통과! 레벨업 시 공격 속도가 정확히 10%씩 증가합니다.")
        return True
    else:
        print("❌ 테스트 실패! 공격 속도 증가가 올바르지 않습니다.")
        return False


def test_weapon_component_direct_access():
    """Test that weapon component values are directly modified."""
    print("\n=== 무기 컴포넌트 직접 확인 테스트 ===")
    
    entity_manager = EntityManager()
    event_bus = EventBus()
    weapon_manager = WeaponManager()
    
    weapon_manager.set_entity_manager(entity_manager)
    event_bus.subscribe(weapon_manager)
    
    # 플레이어 엔티티 생성
    player_entity = entity_manager.create_entity()
    player_id = player_entity.entity_id
    
    entity_manager.add_component(player_entity, PlayerComponent())
    
    # 무기 컴포넌트
    weapon_comp = WeaponComponent(
        weapon_type=WeaponType.SOCCER_BALL,
        damage=25,
        attack_speed=2.0,
        range=300.0,
        last_attack_time=0.0,
    )
    entity_manager.add_component(player_entity, weapon_comp)
    
    print(f"초기 무기 공격 속도: {weapon_comp.attack_speed:.2f}/s")
    
    # 레벨 3으로 올리는 이벤트
    level_up_event = LevelUpEvent.create_from_level_change(
        player_entity_id=player_id,
        previous_level=1,
        new_level=3,
        total_experience=300,
        remaining_experience=0,
    )
    
    event_bus.publish(level_up_event)
    event_bus.process_events()
    
    # 무기 컴포넌트가 직접 수정되었는지 확인
    print(f"레벨 3 후 무기 공격 속도: {weapon_comp.attack_speed:.2f}/s")
    print(f"예상 공격 속도: {2.0 * (1.0 + 2 * 0.1):.2f}/s")
    
    expected = 2.0 * (1.0 + 2 * 0.1)  # 2.4
    if abs(weapon_comp.attack_speed - expected) < 0.01:
        print("✅ 무기 컴포넌트가 직접 수정되었습니다!")
        return True
    else:
        print("❌ 무기 컴포넌트가 수정되지 않았습니다!")
        return False


if __name__ == "__main__":
    try:
        test1_passed = test_attack_speed_increase()
        test2_passed = test_weapon_component_direct_access()
        
        print(f"\n{'='*50}")
        print("📋 테스트 결과 요약:")
        print(f"{'='*50}")
        print(f"🎯 공격 속도 증가 테스트: {'✅ 통과' if test1_passed else '❌ 실패'}")
        print(f"🔧 무기 컴포넌트 수정 테스트: {'✅ 통과' if test2_passed else '❌ 실패'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 모든 테스트 통과! 경험치 획득 시 공격 속도가 10%씩 증가하는 시스템이 완성되었습니다!")
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다. 시스템을 점검해주세요.")
            
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()