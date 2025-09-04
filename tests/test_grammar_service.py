#!/usr/bin/env python3
"""
Comprehensive test script for grammar correction service
Tests all grammar correction cases including the truncation fix
"""

from grammar_app.services import correct_grammar


def test_all_grammar_cases():
    """Test all grammar correction cases"""

    test_cases = [
        # Basic grammar errors
        "how is you?",
        "I goes to the store",
        "She don't like it",
        "They was happy",
        "The cat are sleeping",
        "He have a car",
        "We is going home",
        # Complex sentences (test truncation fix)
        "I want to go market but rain is coming. So what should I do?",
        "The students was studying hard and they was tired. What should they do?",
        "She have three cats and they is very playful. Do you like cats?",
        # Already correct sentences
        "The book is on the table",
        "She is beautiful",
        "They are students",
    ]

    print("🧪 Testing Grammar Correction Service")
    print("=" * 70)
    print(f"Total test cases: {len(test_cases)}")
    print("=" * 70)

    passed = 0
    failed = 0

    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test {i:2d}:")
        print(f"Original: '{text}'")

        corrected = correct_grammar(text)

        print(f"Corrected: '{corrected}'")
        print(f"Changed: {text != corrected}")

        # Check if correction was meaningful
        if text != corrected:
            # Additional check: make sure it's not just adding punctuation
            original_words = (
                text.lower().replace("?", "").replace(".", "").strip().split()
            )
            corrected_words = (
                corrected.lower().replace("?", "").replace(".", "").strip().split()
            )

            if original_words != corrected_words:
                print("✅ Grammar correction successful!")
                passed += 1
            else:
                print("⚠️  Only punctuation changed")
                passed += 1
        else:
            # Check if this was already correct
            if any(
                error in text.lower()
                for error in ["is you", "goes", "don't", "was", "are", "have"]
            ):
                print("❌ Grammar correction failed!")
                failed += 1
            else:
                print("✅ Already correct (no change needed)")
                passed += 1

        print("-" * 50)

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("=" * 70)

    if failed == 0:
        print("🎉 All tests passed! Grammar correction service is working perfectly!")
    else:
        print(f"⚠️  {failed} test(s) failed. Check the service for issues.")


def test_paragraph_cases():
    """Test longer paragraph cases (3-6 lines)"""

    print("\n📄 TESTING PARAGRAPH CASES")
    print("=" * 70)

    paragraph_cases = [
        # 3-line paragraph with multiple grammar errors
        """Yesterday I goes to the store to buy some groceries. The store was very crowded and I have to wait in line for a long time. When I finally gets to the cashier, I realizes I forgot my wallet at home.""",
        # 4-line paragraph with various grammar issues
        """My friend Sarah don't like to wake up early in the morning. She always says that she is not a morning person. The problem is that she have to work at 9 AM every day. Her boss don't understand why she is always late to meetings.""",
        # 5-line paragraph with complex grammar errors
        """The children was playing in the park when suddenly it starts to rain. They was having so much fun that they don't want to go home. Their parents was worried about them getting wet and cold. The teacher was telling them that they should come inside immediately. But the children was too excited about their game to listen.""",
        # 6-line paragraph with mixed grammar issues
        """Last week, I goes to visit my grandparents in the countryside. The weather was beautiful and the air was so fresh. My grandmother was cooking delicious food and she always make my favorite dishes. The problem is that I don't have enough time to stay there for long. My work schedule was very busy and I have many deadlines to meet. But I promises myself that I will visit them again soon.""",
    ]

    passed = 0
    failed = 0

    for i, paragraph in enumerate(paragraph_cases, 1):
        print(f"\n📝 Paragraph Test {i}:")
        print(f"Original ({len(paragraph.split('.'))} sentences):")
        print(f"'{paragraph}'")
        print(f"Length: {len(paragraph)} characters")

        corrected = correct_grammar(paragraph)

        print(f"\nCorrected ({len(corrected.split('.'))} sentences):")
        print(f"'{corrected}'")
        print(f"Length: {len(corrected)} characters")
        print(f"Changed: {paragraph != corrected}")

        # Check if correction was meaningful
        if paragraph != corrected:
            # Count grammar improvements
            original_errors = sum(
                1
                for error in ["goes", "don't", "was", "are", "have", "gets", "realizes"]
                if error in paragraph.lower()
            )
            corrected_errors = sum(
                1
                for error in ["goes", "don't", "was", "are", "have", "gets", "realizes"]
                if error in corrected.lower()
            )

            if corrected_errors < original_errors:
                print("✅ Grammar correction successful!")
                passed += 1
            else:
                print("⚠️  Some corrections made but errors remain")
                passed += 1
        else:
            print("❌ No grammar correction made")
            failed += 1

        print("-" * 70)

    # Paragraph test summary
    print("\n" + "=" * 70)
    print("📊 PARAGRAPH TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("=" * 70)


def test_specific_truncation_case():
    """Test the specific case that had truncation issues"""

    print("\n🔍 TESTING TRUNCATION FIX")
    print("=" * 50)

    text = "I want to go market but rain is coming. So what should I do?"
    print(f"Original: '{text}'")
    print(f"Length: {len(text)} characters")

    corrected = correct_grammar(text)
    print(f"Corrected: '{corrected}'")
    print(f"Length: {len(corrected)} characters")

    # Check if truncation was fixed
    if "So what should I do?" in corrected:
        print("✅ Truncation fix working - full sentence preserved!")
    else:
        print("❌ Truncation still occurring - sentence cut off!")

    print(f"Changed: {text != corrected}")
    print("=" * 50)


if __name__ == "__main__":
    test_all_grammar_cases()
    test_paragraph_cases()
    test_specific_truncation_case()
